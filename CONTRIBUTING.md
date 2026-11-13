# Contributing

## Commits

Conventional Commits, one logical change per commit:

```
feat(policy): deny bcc on send_email
fix(budget): charge before accepting the call
test(eval): add the destructive-action case
docs(adr): record the mock-first decision
```

## Before a PR

```bash
make test    # unit + eval, no network
make lint
make eval    # must be 6/6
```

## Rules

- A new tool without a policy rule is a bug: it will be denied, not executed.
- A change to `policy.py` needs a test that proves the deny path.
- No key, token or customer data in a fixture. The eval cases are synthetic.
