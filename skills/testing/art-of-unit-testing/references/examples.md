# Examples: noise vs signal

Code under test (pseudo-code, same idea in any language):

```
class OrderService(repo, emailGateway, clock):
    place(customerId, items) -> Order
        customer = repo.getCustomer(customerId)          # incoming (stub)
        order = Order.create(customer, items, clock.now()) # in-process domain (real)
        if order.total > 10_000: order.requireApproval()
        repo.save(order)                                  # managed dep (integration test)
        emailGateway.sendConfirmation(customer.email, order.id)  # outgoing unmanaged (mock)
        return order
```

## Noise (reject)

```python
def test_place():                                   # name says nothing
    repo = Mock(); email = Mock(); clock = Mock()
    repo.getCustomer.return_value = customer()
    service = OrderService(repo, email, clock)

    order = service.place(1, [item(5000), item(6000)])

    repo.getCustomer.assert_called_once_with(1)      # asserting a stub
    repo.save.assert_called_once()                  # managed dep, implementation detail
    email.sendConfirmation.assert_called()          # 2nd exit point in same test
    assert order is not None                        # weak assertion
    assert order.total == sum(i.price for i in [item(5000), item(6000)])  # logic in test
```

Problems: 3 mocks, verifies a stub, mixes 3 exit points, re-implements the sum, survives almost any bug in the approval rule.

## Signal (accept)

Triage: `Order` = domain (unit test hard). `OrderService` = orchestration (thin; 1 integration test covers `repo.save`). The approval rule lives in `Order`, so test it there, output-based, no doubles.

```python
def test_order_over_10000_requires_approval():
    sut = make_order(items=[item(price=6_000), item(price=4_001)])

    assert sut.requires_approval is True       # state exit point (Act is the constructor call above)

def test_order_of_exactly_10000_does_not_require_approval():   # boundary, other side
    sut = make_order(items=[item(price=6_000), item(price=4_000)])

    assert sut.requires_approval is False

@pytest.mark.parametrize("items", [[], [item(price=0)]])
def test_order_without_billable_items_is_rejected(items):
    with pytest.raises(EmptyOrderError):
        make_order(items=items)

def make_order(items, customer=None, now=datetime(2026, 1, 1)):  # factory with defaults
    return Order.create(customer or a_customer(), items, now)
```

The only communication-based test, one mock, stubs not verified:

```python
def test_placing_an_order_emails_the_customer_a_confirmation():
    email = Mock()
    sut = OrderService(StubRepo(customer=a_customer(email="ana@x.com")), email, FixedClock())

    order = sut.place(customer_id=1, items=[item(price=100)])

    email.sendConfirmation.assert_called_once_with("ana@x.com", order.id)
```

## Same rules, other languages (shape only)

```ts
// Vitest
it.each([[6000, 4001, true], [6000, 4000, false]])(
  "order of %i + %i requires approval: %s", (a, b, expected) => {
    const sut = makeOrder({ items: [item(a), item(b)] });

    expect(sut.requiresApproval).toBe(expected);
  });
```

```java
// JUnit 5
@ParameterizedTest(name = "order of {0} requires approval: {1}")
@CsvSource({"10001, true", "10000, false"})
void order_approval_threshold(int total, boolean expected) {
    var sut = anOrder().withTotal(total).build();

    assertEquals(expected, sut.requiresApproval());
}
```

```go
// Go table test: the loop only dispatches
func TestOrderApprovalThreshold(t *testing.T) {
    cases := []struct{ name string; total int; want bool }{
        {"over 10000 requires approval", 10001, true},
        {"exactly 10000 does not", 10000, false},
    }
    for _, tc := range cases {
        t.Run(tc.name, func(t *testing.T) {
            sut := newOrder(withTotal(tc.total))

            if got := sut.RequiresApproval(); got != tc.want {
                t.Errorf("RequiresApproval() = %v, want %v", got, tc.want)
            }
        })
    }
}
```

## Mutation check log (what the report should show)

| Test | Mutation | Red? |
|---|---|---|
| order over 10000 requires approval | `>` to `>=` | yes (boundary test catches it) |
| order over 10000 requires approval | threshold 10000 to 20000 | yes |
| placing an order emails confirmation | delete `sendConfirmation` line | yes |
