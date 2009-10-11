from __future__ import with_statement
import pickle
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
		return "t"

class Nil:
	def __init__(self):
		pass

	def __iter__(self):
		return self

	def next(self):
		raise StopIteration

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
			s += expression.__repr__() + " "

		return s

class Quoted:
	def __init__(self, quoted_expression):
		self.quoted_expression = quoted_expression
	
	def eval(self, env):
		return self.quoted_expression

	def __repr__(self):
		return "'%s" % self.quoted_expression

class Dot:
	def __init__(self):
		pass

	def eval(self, env):
		return self

	def __repr__(self):
		return "."

class ListIterator:
	def __init__(self, list):
		self.cell = list

	def __iter__(self):
		return self

	def next(self):
		if isinstance(self.cell, Nil):
			raise StopIteration

		if isinstance(self.cell.cdr, ConsCell) or isinstance(self.cell.cdr, Nil):
			cell = self.cell
			self.cell = self.cell.cdr
			return cell.car
		else:
			cell = self.cell
			self.cell = Nil()
			return cell.car

class ConsCell:
	def __init__(self, car, cdr):
		self.car = car
		self.cdr = cdr

	def __iter__(self):
		return ListIterator(self)

	def __len__(self):
		if isinstance(self.cdr, ConsCell):
			return 1 + len(self.cdr)
		else:
			return 1

	def eval(self, env):
		first = self.first()
		rest = self.rest()

		if isinstance(first, Symbol) and first.name == "defmacro":
			return setq_func(env, rest.first(), Macro(env, rest.rest().first(), rest.rest().rest().first().eval(env)))

		if isinstance(first, Symbol) and first.name == "if":
			if not isinstance(rest.first().eval(env), Nil):
				return rest.rest().first().eval(env)
			else:
				return rest.rest().rest().first().eval(env)

		if isinstance(first, Symbol) and first.name == "lambda":
			return Lambda(env, rest.first(), rest.rest())

		if isinstance(first, Symbol) and first.name == "setq":
			return setq_func(env, rest.first(), rest.rest().first().eval(env))

		#if isinstance(first, Symbol) and first.name == "if":
		#	return 

		return FunctionCall(first, rest).eval(env)

	def first(self):
		return self.car

	def rest(self):
		return self.cdr

	def printlist(self):
		if isinstance(self.cdr, ConsCell):
			return "%s %s" % (self.car, self.cdr.printlist())
		elif isinstance(self.cdr, Nil):
			return self.car
		else:
			return "%s . %s" % (self.car, self.cdr)

	def __repr__(self):
		if isinstance(self.cdr, ConsCell):
			return "(%s %s)" % (self.car, self.cdr.printlist())
		elif isinstance(self.cdr, Nil):
			return "(%s)" % self.car
		else:
			return "(%s . %s)" % (self.car, self.cdr)

def car_func(env, cons_cell):
	return cons_cell.first()

def cdr_func(env, cons_cell):
	return cons_cell.rest()

def cons_func(env, car, cdr):
	return ConsCell(car, cdr)

def listp_func(env, thing):
	if isinstance(thing, ConsCell) or isinstance(thing, Nil):
		return True()
	else:
		return Nil()

def endp_func(env, thing):
	eval_assert(isinstance(thing, ConsCell) or isinstance(thing, Nil), "argument to endp was not a list: %s" % thing)

	if isinstance(thing, Nil):
		return True()
	else:
		return Nil()

def null_func(env, thing):
	if isinstance(thing, Nil):
		return True()
	else:
		return Nil()

def atom_func(env, thing):
	if isinstance(thing, Nil) or isinstance(thing, True) or isinstance(thing, Symbol) or isinstance(thing, Integer):
		return True()
	else:
		return Nil()

def list_func(env, *values):
	if len(values) == 0:
		return Nil()

	reversed = list(values)
	reversed.reverse()

	next = Nil()
	for val in reversed:
		next = ConsCell(val, next)

	return next

def make_list(expressions):
	if len(expressions) == 0:
		return Nil()

	first = prev = ConsCell(expressions[0], Nil())
	dot_next = False
	for exp in expressions[1:]:
		if isinstance(exp, Dot):
			dot_next = True
		elif dot_next:
			dot_next = False
			prev.cdr = exp
		else:
			prev.cdr = ConsCell(exp, Nil())
			prev = prev.cdr
	
	return first

class Macro:
	def __init__(self, env, parameters, expression):
		self.env = env
		self.parameters = parameters
		self.expression = expression

	def eval(self, env):
		return self

	def apply(self, env, args):
		#env = self.env
		eval_assert(len(self.parameters) == len(args), "wrong number of arguments to macro")

		for (param, arg) in zip(self.parameters, args):
			env[param] = arg

		return String("macros are not yet implemented...")

		res = self.expression.eval(env)
		return res.eval(env)

	def __repr__(self):
		return "<macro: %s, %s>" % (self.parameters, self.expression)

class Lambda:
	def __init__(self, env, parameters, expressions):
		self.env = env
		self.parameters = parameters
		self.expression = ExpressionBody(expressions)

	def eval(self, env):
		return self

	def apply(self, env, args):
		#env = self.env
		eval_assert(len(self.parameters) == len(args), "wrong number of arguments to lambda function")

		for (param, arg) in zip(self.parameters, args):
			env[param] = arg.eval(env.parent)

		return self.expression.eval(env)

	def __repr__(self):
		return "<lambda function: %s, %s>" % (self.parameters, self.expression)
	
class NativeFunction:
	def __init__(self, function, name, num_args):
		self.function = function
		self.name = name
		self.num_args = num_args

	def eval(self, env):
		return self

	def apply(self, env, args):
		if self.num_args != -1:
			eval_assert(len(args) == self.num_args, "wrong number of arguments to function %s " % self.name);

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
		function = self.function.eval(env)

		eval_assert(isinstance(function, NativeFunction) or isinstance(function, Lambda) or isinstance(function, Macro), "attempt to call non-function: %s" % function);

		return function.apply(Environment(env), self.args)

	def __repr__(self):
		return "(%s %s)" % (self.function, self.args)

def tokenize(text):
	token_descriptions = [
	("whitespace", "(\s+)"),
	("string", '"((?:\\.|[^"])*)"'),
	("symbol", "([a-zA-Z<>=+\-*/][a-zA-Z0-9<>=+\-*/]*)"),
	("leftparenthesis", "(\()"),
	("rightparenthesis", "(\))"),
	("integer", "(\d+)"),
	("quote", "(')"),
	("dot", "(\.)"),
	("INVALID", "(.+)")]

	pattern = "|".join([token_pattern for (_, token_pattern) in token_descriptions])

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
	
	while not token_stream.empty() and not token_stream.peek().name == "rightparenthesis":
		exp = parse_expression(token_stream)

		expressions.append(exp)

		if isinstance(exp, Dot):
			# list must contain exactly one more value
			parse_assert(not token_stream.empty() and not token_stream.peek().name in ["rightparenthesis", "dot"], "malformed dotted list")
			expressions.append(parse_expression(token_stream))
			break

	parse_assert(not token_stream.empty() and token_stream.pop().name == "rightparenthesis", "missing ) when trying to parse list")

	return make_list(expressions)

def parse_symbol(token_stream):
	parse_assert(token_stream.peek().name == "symbol", "invalid symbol: %s" % token_stream.peek().value);

	return Symbol(token_stream.pop().value)

def parse_constant(token_stream):
	if token_stream.peek().name == "string":
		return String(token_stream.pop().value)
	elif token_stream.peek().name == "integer":
		return Integer(int(token_stream.pop().value))
	else:
		parse_assert(False, "invalid constant: %s" % token_stream.peek().value)

def parse_quoted(token_stream):
	parse_assert(token_stream.peek().name == "quote", "attempted to parse non-quoted as quoted")
	num_quotes = 0

	while not token_stream.empty() and token_stream.peek().name == "quote":
		num_quotes += 1
		token_stream.pop()

	parse_assert(not token_stream.empty(), "quoted empty expression")

	exp = parse_expression(token_stream)

	quoted = Quoted(exp)
	for i in range(num_quotes - 1):
		quoted = Quoted(quoted)
	
	return quoted

def parse_dot(token_stream):
	token_stream.pop()
	return Dot()

def parse_expression(token_stream):
	if token_stream.peek().name == "leftparenthesis":
		return parse_list(token_stream)
	elif token_stream.peek().name == "symbol":
		return parse_symbol(token_stream)
	elif token_stream.peek().name in ["string", "integer"]:
		return parse_constant(token_stream)
	elif token_stream.peek().name == "quote":
		return parse_quoted(token_stream)
	elif token_stream.peek().name == "dot":
		return parse_dot(token_stream)

	parse_assert(False, "garbage found when trying to parse expression: %s of type %s" % (token_stream.peek().value, token_stream.peek().name))

def parse_expression_list(token_stream):
	expressions = []

	while not token_stream.empty():
		expressions.append(parse_expression(token_stream))

	return expressions

def sub_func(env, a, b):
	#eval_assert(len(l) == 2, "function - takes exactly 2 arguments")

	#a = l[0]
	#b = l[1]
	eval_assert(isinstance(a, Integer) and isinstance(b, Integer), "arguments must be ints")
	return Integer(a.value - b.value)

def mul_func(env, a, b):
	eval_assert(isinstance(a, Integer) and isinstance(b, Integer), "arguments must be ints")
	return Integer(a.value * b.value)

def setq_func(env, s, x):
	eval_assert(isinstance(s, Symbol), "must be 2 args with first being a symbol")
	env[s] = x
	return x

def print_func(env, str):
	eval_assert(isinstance(str, String), "must be a string")
	print str.value
	return str

def integer_eq_func(env, a, b):
	eval_assert(isinstance(a, Integer) and isinstance(b, Integer), "arguments must be ints")
	
	if a.value == b.value:
		return True()
	else:
		return Nil()

def integer_lt_func(env, a, b):
	eval_assert(isinstance(a, Integer) and isinstance(b, Integer), "arguments must be ints")

	if a.value < b.value:
		return True()
	else:
		return Nil()

def not_func(env, x):
	if isinstance(x, Nil):
		return True()
	else:
		return Nil()

def and_func(env, a, b):
	if (not isinstance(a, Nil)) and (not isinstance(b, Nil)):
		return True()
	else:
		return Nil()

def or_func(env, a, b):
	if (not isinstance(a, Nil)) or (not isinstance(b, Nil)):
		return True()
	else:
		return Nil()

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
		self.globals[Symbol("t")] = True()
		self.globals[Symbol("nil")] = Nil()
		self.globals[Symbol("-")] = NativeFunction(sub_func, "-", 2)
		self.globals[Symbol("*")] = NativeFunction(mul_func, "*", 2)
		self.globals[Symbol("cons")] = NativeFunction(cons_func, "cons", 2)
		self.globals[Symbol("car")] = NativeFunction(car_func, "car", 1)
		self.globals[Symbol("cdr")] = NativeFunction(cdr_func, "cdr", 1)
		self.globals[Symbol("list")] = NativeFunction(list_func, "list", -1)
		self.globals[Symbol("print")] = NativeFunction(print_func, "print", 1)
		self.globals[Symbol("=")] = NativeFunction(integer_eq_func, "=", 2)
		self.globals[Symbol("<")] = NativeFunction(integer_lt_func, "<", 2)
		self.globals[Symbol("not")] = NativeFunction(not_func, "not", 1)
		self.globals[Symbol("and")] = NativeFunction(and_func, "and", 2)
		self.globals[Symbol("or")] = NativeFunction(or_func, "or", 2)
		self.globals[Symbol("listp")] = NativeFunction(listp_func, "listp", 1)
		self.globals[Symbol("endp")] = NativeFunction(endp_func, "endp", 1)
		self.globals[Symbol("atom")] = NativeFunction(atom_func, "atom", 1)
		self.globals[Symbol("null")] = NativeFunction(null_func, "null", 1)

		self.savable_environment = Environment(self.globals)
		#self.globals[Name("inc")] = Lambda(List([List([Name("lol")]), Name("add"), Name("lol"), Integer(1)]))
		#self.globals[Name("yes")] = Lambda(List([List([]), Name("#t")]))
		#self.globals[Name("no")] = Lambda(List([List([]), Name("nil")]))

	def trig_lisp(self, bot, source, target, trigger, argument):
		try:
			retn = str(lisp(self.savable_environment, argument))
			self.save()
			return retn
		except LispError as e:
			return str(e)

	def save(self):
		with open('data/lisp_state.txt', 'w') as file:
			p = pickle.Pickler(file)

			self.savable_environment.parent = None
			p.dump(self.savable_environment)
			self.savable_environment.parent = self.globals

	def on_load(self):
		try:
			with open('data/lisp_state.txt') as file:
				unp = pickle.Unpickler(file)

				self.savable_environment = unp.load()
		except:
			self.savable_environment = Environment(self.globals)

		self.savable_environment.parent = self.globals
	
	def on_unload(self):
		self.savable_environment = Environment(self.globals)

import sys

command = LispCommand()
#print command.trig_lisp("bot", "source", "target", "trigger", sys.argv[1])
#print command.savable_environment
#print command.globals

