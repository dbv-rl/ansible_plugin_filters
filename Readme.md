# Ansible Plugins filter

This repository contains filters as extension for Ansible.

## `is_due`

method: is_due(datestring, operator)

> Checks is a given datestring of format 'YYYY-mm-dd' is due based on `operator`.
> Default: operator = '==', which means it's matching against today.
> Valid operators: `==`, `>`, `>=`, `<=`, `<`, `!=`.
> The date provided with datestring is checked against the current date
> $today $operator $datestring

example:

```yaml
---
# Only runs on 2022-01-01
- debug: msg="foobar"
  when: "'2022-01-01' | is_due"

# Only runs after 2022-01-01
- debug: msg="foobar"
  when: "'2022-01-01' | is_due(operator='>')"
```

## `is_future`

method: is_future(datestring)

> Checks if a given datestring of format 'YYYY-mm-dd' is in the future.
> The date provided with datestring is checked against the current date.

example:

```yaml
---
# Only runs before 2022-01-01
- debug: msg="foobar"
  when: "'2022-01-01' | is_future()"
```

## `is_past`

method: is_past(datestring)

> Checks if a given datestring of format 'YYYY-mm-dd' is in the past.
> The date provided with datestring is checked against the current date.

example:

```yaml
---
# Only run after 2022-01-01
- debug: msg="var"
  when: "'2022-01-01' | is_past()"
```

## `is_today`

method: is_today(datestring)

> Checks if a given datestring of format 'YYYY-mm-dd' is today.
> The date provided with datestring is checked against the current date.

## `is_today_or_future`

method: is_today_of_future(datestring)

> Checks if a given datestring of format ('YYYY-mm-dd') is either today or lies in the future.
> The date provided with datestring is checked against the current date.

```yaml
---
# Runs only before and at 2022-01-01
- debug: msg="foobar"
  when: "'2022-01-01' | is_today_or_future"
```

## `is_today_or_past`

method: is_today_or_past(datestring)

> Checks if a given datestring of format ('YYYY-mm-dd' is either today or lies in the past.
> The date provided with datestring is checked against the current date.

example:

```yaml
# Runs only at 2022-01-01 and after.
- debug: msg="var"
  when: "'2022-01-01' | is_today_or_past"
```

## TODO

* Add `is_past_or_future`. Probably rarely used, but: who knows.
