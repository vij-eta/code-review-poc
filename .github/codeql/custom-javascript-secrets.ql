import javascript

predicate boolean looksLikeSecret(string value) {
  value.matches(r"(?i).*(api[_-]?key|token|secret|password).{0,20}=[\'\"]{1}[A-Za-z0-9-_=+]{10,}[\'\"]{1}")
}

from VariableDeclarator v, string value
where v.getInitializer().toString(value) and looksLikeSecret(value)
select v, "Possible hardcoded secret detected: " + value
