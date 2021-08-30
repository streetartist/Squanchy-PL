#-------------------------------------------------------------------------------
# Copyright (C) 2018 Gabriel Rodriguez Canal
# Copyright (C) 2018 Marcos V. Conde
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------


import sys
import re
import json
import time
import visualiser as visu
from statistics import mean 
import os
from myeval import Eval


# symbol: constans, operators, ids, keywords
# symbol_table = {symbol : symbol_class}

token_list = []

symbol_table = {}

names_map = {"+":"Add","-":"Sub","*":"Mul","/":"Div",
        "**":"Power","%":"Mod","and":"And","or":"Or",
        "&":"Bitand","^":"Bitxor",
        "<<":"LeftShift",">>":"RightSift","lambda":"Lambda",
        "if":"IfExp","[":"List",":":"Assign",".":"Access",":=":"Let","<-":"Data",
        "\\t":"TAB","\\n\\t":"INDENT","\\n":"NEWLINE"}



#--------------------------------------------------------------------------------------------
# NAME SPACE | SCOPE

class Scope:

    """Clase espacio de nombres. Scope
    See https://pythonspot.com/scope/
    Modeliza un espacio donde las variables son definidas y accesibles,
    pudiendo haber variables locales y globales.
    """

    def __init__ (self):

        self.names = {}

    def define (self,n):

        """ Define nuevas variables en el espacio <self>.
        Transforma el token de un nombre a una variable.
        Error si la variable ya esta en el espacio, o si el nombre dado ya esta reservado.
        """
        t = self.names[n.value]
        if t:
            raise NameError ("Already defined or reserved %r" % n)

        self.names[n.value] = n
        n.reserved = False
        name.nud = lambda self: self
        n.led = None
        n.lbp = 0
        n.space = space
        return n

    def find (self,name):

        """Encuentra la defincion de <nombre>, el valor.
        Busca en el espacio actual <self> y si no lo encuentra sube niveles,
        en ultima instancia devuelve valor en symbol_table si no lo encuentra.
        Además comprueba si <nombre> no esta undefined o es una funcion.
        """

        return self.names[name]
        """
        e = self
        while 1:
            o = e.names[name]
            if o and o.arity != "function":
                return e.names[name]
            
            e = e.parent
            if not e:
                o = symbol_table[name];
                if o.arity != "function": return o
                else: return symbol_table["Name"] 
		"""

    def pop (self):

        """Asciende un nivel en la jerárquia del espacio de nombres.
        """
        scope = self.parent


    def reserve(self,id,value):

        """Indica que <nombre> se ha usado o es una palabra reservada
        en el espacio actual <self>.
        Por ejemplo "if" será reservada y no podrá usarse como nombre de variable o funcion.
        Los nombres se reservan localmente solo cuando se usen como palabras reservadas.

        """

        try:
        	t = self.names[id]
        	if t:
        		self.names[id] = value # update value
        		#raise NameError ("Already defined")

        except KeyError:
            self.names[id] = value
            #name.reserved = True


    def __repr__(self):
        return json.dumps(self.names)


def new_space ():
    s = space
    space = Scope()
    space.parent = s
    return space;

SCOPE = Scope()


#--------------------------------------------------------------------------------------------


def symbol(id, bp=0):

    """Creates a new class for token <id> (if necessary)

        Param:
        id -- token's id or symbol
        bp -- binding power

        Return:
        Protoclass -- Symbol <id> Class. Sample: token's id = "+" 
        then return the symbol's <+> class, called SymClass_+

    """

    try:
        Protoclass = symbol_table[id]
    except KeyError:

        class Protoclass:

            """Prototype Class model for grammar symbols.
            Default nud and led methods.
            Default attributes: lbp, id, value, arity ...
            """

            # Class attributes

            lbp = bp
            value = id


            def __init__ (self):

                self.first = self.second = self.third = None
                self.id = id
                self.arity = None
                self.reserved = False 
                try : self.name = names_map[self.id]
                except KeyError: self.name= self.id    


            def nud (self):
                """Default nud method.
                Check prefix
                """
                print ("problema, NUD no definido ", self.id)
                if self.name == "INDENT":
                    raise IndentationError ('Incorrect use of TABS.')


            def led (self,left):

                """Default led method.
                Check infix and infix_r.
                """
                print ("problema, LED no definido ", self.id)
                raise SyntaxError("Syntax error (%r)." % self.id)


            def __repr__(self):
                               
                out = [self.first, self.second, self.third]
                out = map(str, filter(None, out))

                if self.arity == 1:
                    return self.name +"("+ "".join(out) + ")"

                elif self.id == "Name" or self.id == "Const":
                    return "%s (%s)" % (self.id, self.value)

                return self.name + "("+ ",".join(out) + ")"

        Protoclass.__name__ = "SymClass_" + id
        symbol_table[id] = Protoclass

    else:
        Protoclass.lbp = max(bp, Protoclass.lbp)

    return Protoclass



def advance (id=None):

    """Genera la instancia el token siguiente según su correspondiente clase.
    Permite comparar el id del siguiente con un id pasado por párametro.

    Párametros:
    id -- id del token que vamos a instanciar (next token). 
        Si id = None simplemente se instanciará el siguiente token.
        Si id tiene un valor, se compmrobará antes de instanciar.
    """

    global token
    if id and token.id != id:
        raise SyntaxError("Expected %r" % id)

    if token.id == "(end)": pass
    else:
        token = next()


def ignore (id=None):

    """ MOD of advance function. Ignores token <id>, advance until sees token different than <id>
    """

    global token
    while token.id == id:
        token = next()
    if token.id == "(end)": pass


def add_method(symbol_class):

    """Decorator. Add <fn> as <symbol_class> method, if <symbol_class> exists.
    """
    assert symbol_class in symbol_table.values()
    def new_method(fn):
        setattr(symbol_class, fn.__name__, fn) # (class, function name, value = funcion)
    return new_method



def prefix(id, bp):

    """
    Prefix expressions.
    Arity 1.
    Examples: +,-, not => UnaryAdd, UnaryMinus, Not
    """

    names = {"+":"UnaryAdd", "-":"UnarySub","not":"Not"}
    def nud(self):
        self.first = parse(bp)
        self.name = names[self.id]
        self.solve = self.first
        self.arity = 1
        return self
    symbol(id).nud=nud


def infix(id,bp):
    
    def led(self, left):
        self.first = left
        self.second = parse(bp)
        self.arity = 2
        return self
    symbol(id,bp).led=led
 


# special infix case: right associative
def infix_r(id,bp):
    def led(self, left):
        self.first = left
        self.second = parse(bp-1) # solves right associative
        self.arity = 2
        return self
    symbol(id,bp).led=led



# Fill Symbol Table
# To understand bp and operator precedence:
# See https://docs.python.org/3/reference/expressions.html | 6.16. Operator precedence

symbol("Const")
symbol("Name")
symbol("(end)")


# OPERATORS

prefix("+", 130); prefix("-", 130); prefix("not", 50)

infix("+",110); infix("-",110)
infix("*",120); infix("/",120)
infix("%",120); infix("not", 60)
infix("<<",100); infix(">>",90)
infix("<",60); infix("<=",60)
infix(">",60); infix(">=",60)
infix("!=",60); infix("=",60) # "different" and "equal" symbols

infix_r("**",140); infix_r("or",20); infix_r("and",40)


# Constants
symbol("global",1000)

# Lists
symbol("[", 150);symbol("]")
symbol(".",150) #index

# Parentheses and Tuples
symbol("(", 150);symbol(")");symbol(",")

# Statement
symbol("::"); symbol("->"); infix("<-",10)
symbol(":",10); symbol(":=",15)
symbol("|")
symbol("lambda",20)
symbol("while",20)
symbol("if", 20); symbol("then",15); symbol("else")

symbol(")"); symbol(",")
symbol("}");symbol("{"); symbol(",");symbol(":");symbol(";") 
symbol("\\n\\t"); symbol("\\n") ; symbol("\\t")

symbol("Module")



#--------------------------------------------------------------------------------------------
# Add NUD and LED methods to each symbol using decorator <add_method> (if necessary)
# Remember each symbol has his own class with default atributtes and methods created above
# so we may have to change them.


symbol("Const").nud = lambda self: self


#symbol("Const").solve = lambda self: self.value

"""
@add_method(symbol("Name"))
def nud (self):

    #print (SCOPE)
    if self.value not in SCOPE.names:
        return self
    else:
        # FunCall
        self.name = self.id = "FunCall"
        self.first = token
        print ("arg:",self.first)
        advance()
        return self
"""
symbol("Name").nud = lambda self: self # !!!


#--------------------------------------------------------------------------------------------

def constant(id,value):
    @add_method(symbol(id))
    def nud(self):
        self.id = self.name = "Const"
        self.value = value
        SCOPE.reserve(id,value)
        return self

constant("null",None)
constant("True",1)
constant("False",0)
constant("pi", 3.141592653589793)



# global Name -> accessible from any SCOPE
@add_method(symbol("global"))
def nud (self):
    self.first = token # var
    advance("Name")
    constant(self.first.value,None)
    return self


def assigment (self,left):
    #print ("Estoy en assigment")
    self.first = left;
    self.second = parse(self.lbp-1)
    self.arity = 2
    try:
        SCOPE.reserve(self.first.value,Eval(self.second,SCOPE))
    except:
        SCOPE.reserve(self.first.value,"test-mode")
    #SCOPE.reserve(self.first.value,"test-mode")
    #print ("son:",self.first.value,Eval(self.second))
    #print (SCOPE)
    return self

symbol(":").led = assigment
symbol(":=").led = assigment


# a <- { elem1: int, elem2: Dub, elem3:string}  => is structure a 
# a <- []  => a is array
# a: {..} => a is dic 

#--------------------------------------------------------------------------------------------
# LISTS
# expression_list ::=  [expressions...]

@add_method(symbol("["))
def nud(self):
    self.first = []
    if token.id != "]":
        while 1:
            ignore(NEWLINE);ignore(INDENT);ignore(TAB)
            #assert token.id == "Const"
            #self.first.append(token)
            #advance()
            #if token.id == "]":break
            self.first.append(parse()) # check parse is an expression

            ignore(NEWLINE);ignore(INDENT);ignore(TAB)
            if token.id != ",": break
            advance(",")

    advance("]")
    self.arity = 1
    self.name = "List"
    return self


#--------------------------------------------------------------------------------------------
# TUPLES
# expression_tuple ::=  (expressions...)

@add_method(symbol("("))
def nud(self):
    self.first = []
    if token.id != ")":
        while 1:
            if token.id == ")":
                break
            #self.first.append(token)
            self.first.append(parse())
            if token.id != ",":
                break
            advance(",")
    advance(")")

    if len(self.first) > 1:
        self.name = "Tuple"
        return self # tuple

    elif len(self.first) == 1:
    	return self.first[0] # expr
    else:
        raise SyntaxError ("Bad Tuple")


#--------------------------------------------------------------------------------------------
# Item access. INDEX

# expression_access ::= (List|Tuple).Const
# !!! list,tuples,dic & types

@add_method(symbol("."))
def led(self, left):
    if token.id != "Const":
        SyntaxError("Expected numeric index.")
    self.first = left
    self.second = token
    advance()
    return self



#--------------------------------------------------------------------------------------------
# LAMBDA FUNCTION

# lambda [parameter_list]:: expression
# lambda [parameter_list]:: expression_nocond


@add_method(symbol("lambda"))
def nud(self):
    self.first = [] # arg
    if token.id != "::":
        parameter_list(self.first)
    if len(self.first )==0:
        raise SyntaxError ("Bad lambda, no arguments")
    advance("::")
    self.second = parse() # tiene que ser una expression
    return self


def parameter_list(list):
    while 1:
        if token.id != "Name":
            SyntaxError("Expected a parameter Name.")
        list.append(token)
        advance()
        if token.id == "::": break


#--------------------------------------------------------------------------------------------
# STATEMENTS | BLOCK


"""
program : Module
Module : statement|block
block : statement_list | statement  [end_block] statement_list
statement_list : statement|statement [end_stmt] statement_list
statement : simple_statement| assign_statement | empty
empty: 

"""

TAB = "\\t"
INDENT = "\\n\\t"
NEWLINE = "\\n"
SEMICOLON = ";"
end_stmt = [INDENT,"(end)",SEMICOLON]


def statement (end_block):

    """Parsea un statement hasta llegar a <end_stmt> o <end_block>
    """


    if (token.id in ["while","if","else","then"]):
        t = token
        advance()
        return t.nud()

    statement = parse()

    if token.id in end_block:
        pass
    elif token.id in end_stmt: advance(token.id)
    else:
        raise SyntaxError ("Expected %r" % end_stmt)

    return statement
		


def statement_list (end_block=[NEWLINE,"(end)"]):
    
    """Parsea statements hasta llegar a <end_block>.
        Return:
            - statement
            - stmt = array of statements
            - None si no hay statement
    """

    stmt = [] # array of statements

    while 1:

        if token.id in end_block :
            break
        ignore(INDENT)
        ignore(TAB)

        """
        for k in range (1,level):
            try:
                advance(TAB)
            except:
                raise IndentationError('Expected TAB but found "%s" '% token)
        """

        s = statement(end_block) # un solo statement
        if s:
            stmt.append(s)
        ignore(INDENT)

    if len(stmt) == 0: return None
    elif len(stmt) == 1: return [stmt[0]] # s
    else: return stmt


def block (key=None):
    t = token
    advance(key)
    ignore(INDENT) 
    return t.nud()


@add_method(symbol("::"))
def nud (self):
    a = statement_list()
    return a


#--------------------------------------------------------------------------------------------
# FUNCTION CALLS & FUNCTION DECLARATION

"""
FUNCTION_SKELETON =
    {name} {args} -> {return} :: {body}
"""


@add_method(symbol("("))
def led(self,left):

    self.first = left
    self.second = []
    arg = []
    ret = []

    if token.id != ")":
        while 1:
            if token.id == ")":break
            arg.append(parse())
            if token.id != ",":break
            advance(",")

    advance(")")
    self.second.append(arg)

    # sería en el scope de la función no en el general

    """
    for i in arg:
        name = self.first.value+"_"+i.value
        SCOPE.reserve(name,"undefined")
    """

    if self.first.value in SCOPE.names:
        #funcall
        #print (self.first)
        self.third = None   
        self.arity = "2"
        self.name = "CallFunc"
        self.id = self.name
        return self


    #SCOPE.new (left.value,left.value)
    #print (SCOPE)
    
    try:
        advance ("->")
    except:
        self.third = None   
        self.arity = "2"
        self.name = "CallFunc"
        self.id = self.name
        return self
    #t = token
    #advance()

    ret.append(parse())
    #ret.append(t.nud())
    self.second.append(ret)

    # statement
    try :
        self.third = block("::")
        self.arity = "statement"
        
    except SyntaxError:
        pass

    self.name = "Function"
    self.id = self.name

    return self


#--------------------------------------------------------------------------------------------
# WHILE statement

symbol("while").arity = "statement"
symbol("while").name = "While_stmt"

@add_method(symbol("while"))
def nud (self):

    self.first = parse(20)
    self.second = block("::")

    if self.second == None:
        raise WhileError ('While Statement Error. No statement found after ::')

    return self

#--------------------------------------------------------------------------------------------
# IF-THEN-ELSE statement

symbol("if").arity = "statement"

@add_method(symbol("then"))
def nud (self):
    stm = statement_list(["(end)","else",NEWLINE])
    return stm


@add_method(symbol("else"))
def nud (self):
    a = statement_list()
    return a


@add_method(symbol("if"))
def nud(self):
    self.first = parse(20)
    ignore(NEWLINE); ignore(INDENT)

    try :
        self.second = block("then")
    except:
        raise IfError ('Expected "then" but found "%s" '% token)

    if self.second == None :
        raise IfError ('IF-THEN Statement Error. No Statement found after "then"')

    ignore(NEWLINE)
    if token.id == "else":
        self.third = block("else")
        if self.third == None :
            raise IfError('IF-THEN-ELSE Statement Error. No Statement found after "else"')

    self.arity = "statement"
    return self


#--------------------------------------------------------------------------------------------
# MODULE/PROGRAM statement

def module ():
    program = []

    ignore (NEWLINE)
    if token.id != "(end)":
        while 1:
            ignore (NEWLINE)
            #ignore (INDENT)
            ignore (SEMICOLON)
            if token.id == "(end)": break
            if token.id == NEWLINE: ignore(NEWLINE)
            program.append(parse())

    advance("(end)")
    return program


@add_method(symbol("Module"))
def nud (self):
    self.first = module()
    return self


@add_method(symbol("Module"))
def __repr__ (self):
    out = self.first
    out = map(str, out)
    return "Module [ \n\n\t"+ "\n\n\t".join(out) +"\n]"



#--------------------------------------------------------------------------------------------
# LEXER CALL

def tokenize(program):

    """
    # Genera una instancia 'atom' para la clase asociada al token obtenido mediante tokenize_python
    # (tokenize module). Ver symbol_table.
    """

    from lexer import lexer

    for token in lexer(program):

    	if token.id == "number" or token.id == "string":
    		Clase_token = symbol_table["Const"]
    		atom = Clase_token()
    		atom.value = token.value

    	else:

    		Clase_token = symbol_table.get(token.value)

    		if Clase_token:
    			atom = Clase_token()

    		elif token.id == "Name":

    			Clase_token = symbol_table[token.id]
    			atom = Clase_token()
    			atom.value = token.value
    		else:
    			raise SyntaxError("Unknown operator (%r)" % token.value)

    	yield atom


#--------------------------------------------------------------------------------------------
# PARSER ENGINE


def parse(rbp=0):

    """
    Pratt parser implementation.
    See "Top Down Operator Precedence" (section 3: Implementation, pág 47)
    """

    global token
    t = token
    advance()
    left = t.nud()

    while rbp < token.lbp:
        t = token
        advance()
        left = t.led(left)
    return left



def ast(program):

    """Creates AST using Pratt's Parser
    """

    global token,next,level

    next = tokenize(program).__next__ 
    token = next()
    level = 0
    tree = parse()
    return tree,SCOPE
 

#--------------------------------------------------------------------------------------------
# ERRORS

class WhileError(Exception):
    pass

class IfError(Exception):
    pass

class IndentationError(Exception):
    pass

#--------------------------------------------------------------------------------------------
# OPTIONS


def console ():

    """Interactive console for testing. Must change lexer's code, see debugging comments.
    -- commands:
        exit
        clear
    """

    try:
        while True:
            expr = input (">> ")
            if expr == "exit": exit()
            if expr == "clear": 
                os.system('clear')
                console()
            print (ast(expr)[0].first[0])

    except Exception as e:
        print (e.args[0])
        console()


if "--terminal" in sys.argv:

    """Interactive terminal for testing
    """

    print ("Squanchy PL console test")
    print ("v1.1","\n")
    console()


if "--img" in sys.argv:

    """Test tree visualisation.
    """
    program = input (">> ")
    tree,scope = ast(program)
    print (program, "-> ",tree,"\n")
    visu.visualise(tree)


if "--in" in sys.argv:
    
    """Test input
    """

    f = open("code.sqy")
    program = f.read()
    f.close()

    program = program.replace("\n","\\n").replace("\t","\\t")

    tree,scope = ast(program)
    print ("\n",tree)
    print ("\n",scope)
    

if "--benchmark" in sys.argv:
    factor = 1
    program = '1+1+1+1+1+1+1+1+1'*10000

    measure = []

    for i in range(factor):
        measure.append([])
        for j in range(1000):
            start = time.time()
            ast(program)
            end = time.time()
            measure[i].append(float(end-start))
        program = ((program + '+')*10)[:-1]

    print("Time: ", list(map(lambda x: mean(x), measure)))



def main():
	pass


if __name__ == "__main__":
	main()








