from plugins import Plugin
from commands import Command

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
			eval_assert(False, "couldn't find key '%s'." % key)

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
			
class Symbol:
	def __init__(self, name):
		self.name = name

	def eval(self, env):
		return env[self]

	def __hash__(self):
		return self.name.__hash__()

	def __eq__(self, other):
		return self.name.__eq__(other.name)

	def __repr__(self):
		return self.name

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

		if isinstance(first, Symbol) and first.name == "lambda":
			return Lambda(env, rest)

		if isinstance(first, Symbol) and first.name == "setq":
			return setq_func(env, restfirst(), rest.rest().first().eval(env))

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
	("symbol", "([a-zA-Z+\-*/][a-zA-Z0-9+\-*/]*)"),
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

def parse_list(token_stream):
	parse_assert(token_stream.pop().name == "leftparenthesis", "missing ( when trying to parse list")

	expressions = []
	
	while not token_stream.peek().name == "rightparenthesis":
		expressions.append(parse_expression(token_stream))

	parse_assert(token_stream.pop().name == "rightparenthesis", "missing ) when trying to parse list")

	return List(expressions)

def parse_symbol(token_stream):
	if token_stream.peek().name == "symbol":
		return Symbol(token_stream.pop().value)
	else:
		parse_assert(False, "invalid symbol")

def parse_constant(token_stream):
	if token_stream.peek().name == "string":
		return String(token_stream.pop().value)
	elif token_stream.peek().name == "integer":
		return Integer(int(token_stream.pop().value))
	else:
		parse_assert(False, "invalid constant")

def parse_expression(token_stream):
	if token_stream.peek().name == "leftparenthesis":
		return parse_list(token_stream)
	elif token_stream.peek().name == "symbol":
		return parse_symbol(token_stream)
	elif token_stream.peek().name in ["string", "integer"]:
		return parse_constant(token_stream)

	parse_assert(False, "garbage found when trying to parse expression: %s of type %s" % (token_stream.peek().value, token_stream.peek().name))

def parse_expression_list(token_stream):
	expressions = []

	while not token_stream.empty():
		expressions.append(parse_expression(token_stream))

	return expressions

def sub_func(env, l):
	a = l.first()
	b = l.rest().first()
	eval_assert(isinstance(a, Integer) and isinstance(b, Integer), "arguments must be ints")
	return Integer(a.value - b.value)

def setq_func(env, l):
	s = l.first()
	x = l.rest().first()
	eval_assert(isinstance(s, Symbol), "must be 2 args with first being a symbol")
	env[s] = x
	return x

class TokenStream:
	def __init__(self, tokens):
		self.tokens = tokens
		self.current_index = 0

	def peek(self):
		return self.tokens[self.current_index]

	def pop(self):
		token = self.peek()
		self.current_index += 1
		return token

	def empty(self):
		return self.current_index == len(self.tokens)

def lisp(env, text):
	tokens = tokenize(text)
	expressions = parse_expression_list(TokenStream(tokens))

	return expressions[0].eval(env)

class LispCommand(Command): 
	def __init__(self):
		self.globals = Environment()
		self.globals[Symbol("#t")] = True()
		self.globals[Symbol("nil")] = Nil()
		self.globals[Symbol("-")] = NativeFunction(sub_func)
		#globals[Name("inc")] = Lambda(List([List([Name("lol")]), Name("add"), Name("lol"), Integer(1)]))
		#globals[Name("yes")] = Lambda(List([List([]), Name("#t")]))
		#globals[Name("no")] = Lambda(List([List([]), Name("nil")]))

	def trig_lisp(self, bot, source, target, trigger, argument):
		try:
			return str(lisp(self.globals, argument))
		except LispError as e:
			return str(e)

import sys
print lisp(sys.argv[1])
