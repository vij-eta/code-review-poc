import python

predicate boolean looksLikeSecret(string value) {
  value.matches(r"(?i).*(api[_-]?key|token|secret|password).{0,20}=[\'\"]{1}[A-Za-z0-9-_=+]{10,}[\'\"]{1}")
}

from AssignExpr assign, string value
where assign.getRight().toString(value) and looksLikeSecret(value)
select assign, "Possible hardcoded secret detected: " + value
