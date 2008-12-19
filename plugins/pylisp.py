import re

class LispError:
	def __init__(self, msg):
		self.msg = msg

	def __repr__(self):
		return "%s: %s" % (self.__class__.__name__, self.msg)

class TokenizeError(LispError):
	def __init__(self, msg):
		LispError.__init__(self, msg)

class ParseError(LispError):
	def __init__(self, msg):
		LispError.__init__(self, msg)

class EvalError(LispError):
	def __init__(self, msg):
		LispError.__init__(self, msg)

def tokenize_assert(expr, msg):
	if not expr:
		raise TokenizeError(msg)

def parse_assert(expr, msg):
	if not expr:
		raise ParseError(msg)

def eval_assert(expr, msg):
	if not expr:
		raise EvalError(msg)


class Token:
	def __init__(self, name, value):
		self.name = name
		self.value = value

	def __repr__(self):
		return '%s: "%s"' % (self.name, self.value)

class Environment:
	def __init__(self, parent = None):
		self.parent = parent
		self.dictionary = {}

	def __getitem__(self, key):
		if key in self.dictionary:
			return self.dictionary[key]
		elif self.parent:
			return self.parent[key]
		else:
			eval_assert(False, "couldn't find key %s" % key)

	def __setitem__(self, key, value):
		self.dictionary[key] = value

	def __repr__(self):
		s = self.dictionary.__repr__()
		if self.parent:
			s += " %s" % self.parent 
	
		return s

class True:
	def __init__(self):
		pass

	def eval(self, env):
		return self

	def __hash__(self):
		return True.__hash__()

	def __eq__(self, other):
		return isinstance(other, True)

	def __repr__(self):
		return "#t"

class Nil:
	def __init__(self):
		pass

	def eval(self, env):
		return self

	def __hash__(self):
		return None.__hash__()

	def __eq__(self, other):
		return isinstance(other, Nil)

	def __repr__(self):
		return "nil"
			
class Name:
	def __init__(self, name):
		self.name = name

	def eval(self, env):
		return env[self]

	def __hash__(self):
		return self.name.__hash__()

	def __eq__(self, other):
		return self.name.__eq__(other.name)

	def __repr__(self):
		return "%s" % self.name

class String:
	def __init__(self, value):
		self.value = value

	def eval(self, env):
		return self

	def __hash__(self):
		return self.value.__hash__()

	def __eq__(self, other):
		return self.value.__eq__(other.value)

	def __repr__(self):
		return '"%s"' % self.value
class Integer:
	def __init__(self, value):
		self.value = value

	def eval(self, env):
		return self

	def __hash__(self):
		return self.value.__hash__()

	def __eq__(self, other):
		return self.value.__eq__(other.value)

	def __repr__(self):
		return "%i" % self.value

class ExpressionBody:
	def __init__(self, expressions):
		self.expressions = expressions

	def eval(self, env):
		retn = None
		for expression in self.expressions:
			retn = expression.eval(env)

		return retn

	def __repr__(self):
		s = ""
		for expression in self.expressions:
			s += expression.__repr__()

		return s

class List:
	def __init__(self, expressions):
		self.expressions = expressions

	def eval(self, env):
		first = self.first()
		rest = self.rest()

		if isinstance(first, Name) and first.name == "lambda":
			return Lambda(env, rest)

		return FunctionCall(first, rest).eval(env)

	def __len__(self):
		return len(self.expressions)

	def __getitem__(self, index):
		return self.expressions[index]

	def first(self):
		return self.expressions[0]

	def rest(self):
		return List(self.expressions[1:])

	def __repr__(self):
		s = "("
		i = 0
		for expression in self.expressions:
			if i:
				s += " "
			s += expression.__repr__()
			i += 1
		s += ")"

		return s

class Lambda:
	def __init__(self, env, expressions):
		self.env = env
		self.parameters = expressions.first()
		self.expression = ExpressionBody(expressions.rest())

	def eval(self, env):
		return self

	def apply(self, env, args):
		env = self.env
		eval_assert(len(self.parameters) == len(args), "wrong number of arguments to function")

		for i in range(len(args)):
			env[self.parameters[i]] = args[i].eval(env.parent)

		return self.expression.eval(env)

	def __repr__(self):
		return "<lambda function>"
	
class NativeFunction:
	def __init__(self, function):
		self.function = function

	def eval(self, env):
		return self

	def apply(self, env, args):
		evaled_args = []
		for arg in args:
			evaled_args.append(arg.eval(env))

		return self.function(env, *evaled_args)

	def __repr__(self):
		return "%s" % self.function

class FunctionCall:
	def __init__(self, function, args):
		self.function = function
		self.args = args

	def eval(self, env):
		return self.function.eval(env).apply(Environment(env), self.args)

	def __repr__(self):
		return "(%s %s)" % (self.function, self.args)

def tokenize(text):
	token_descriptions = [
	("whitespace", "(\s+)"),
	("string", '"((?:\\.|[^"])*)"'),
	("name", "([a-zA-Z]+)"),
	("leftparenthesis", "(\()"),
	("rightparenthesis", "(\))"),
	("integer", "(\d+)"),
	("quote", "(')"),
	("INVALID", "(.+)")]

	pattern = ""

	for name, token_pattern in token_descriptions:
		if pattern:
			pattern += "|"
		
		pattern += token_pattern

	matches = re.findall(pattern, text)

	tokens = []

	for match in matches:
		i = 0
		for group in match:
			if i > 0 and group:
				tokens.append(Token(token_descriptions[i][0], group))
				break
			i += 1

	return tokens

def get_expressions(tokens, start_index, end_index):
	expressions = []

	i = start_index
	while i <= end_index:
		token = tokens[i]
		if (token.name == "string"):
			expressions.append(String(token.value))
		elif (token.name == "integer"):
			expressions.append(Integer(int(token.value)))
		elif (token.name == "name"):
			expressions.append(Name(token.value))
		elif (token.name == "leftparenthesis"):
			parenthesislevel = 0
			for j in range(i, end_index+1):
				if tokens[j].name == "leftparenthesis":
					parenthesislevel += 1
				elif tokens[j].name == "rightparenthesis":
					parse_assert(parenthesislevel, "unexpected )")
					parenthesislevel -= 1
					if not parenthesislevel:
						expressions.append(List(get_expressions(tokens, i+1, j-1)))

						i = j
						break
			parse_assert(not parenthesislevel, "couldn't find matching )")
		else:
		  	parse_assert(False, "unknown token: %s (%s)" % (token.name, token.value))
		i += 1

	parse_assert(len(expressions), "no expressions found")

	return expressions

def add_func(env, a, b):
	eval_assert(isinstance(a, Integer) and isinstance(b, Integer), "arguments must be ints")
	return Integer(a.value + b.value)

def lisp(text):
	tokens = tokenize(text)
	expressions = get_expressions(tokens, 0, len(tokens)-1)

	globals = Environment()
	globals[Name("#t")] = True()
	globals[Name("nil")] = Nil()
	globals[Name("add")] = NativeFunction(add_func)
	#globals[Name("inc")] = Lambda(List([List([Name("lol")]), Name("add"), Name("lol"), Integer(1)]))
	#globals[Name("yes")] = Lambda(List([List([]), Name("#t")]))
	#globals[Name("no")] = Lambda(List([List([]), Name("nil")]))

	return expressions[0].eval(globals)
