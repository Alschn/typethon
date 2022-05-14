# TKOM - Interpreter języka `Typethon`

## Opis

Typethon to wymyślony język przypominający składnią języki Python i Typescript. Pozwala na definiowanie zmiennych
mutowalnych, niemutowalnych, a także "nullowalnych". Obsługuje funkcje anonimowe.

## Założenia

- język **silnie** i **statycznie** **typowany**
- obsługuje typy danych: `int`, `float`, `str`, `bool`, `func`
- obsługuje "nullowalność" zmiennych, operator `?:` oraz specjalną wartość `null`
- zmienne mogą być mutowalne lub niemutowalne - `let` vs `const`
- operatory arytmetyczne `+`, `-`, `*`, `/`, `%`, `>`, `>=`, `<`, `<=`, `==`, `!=`
- operatory logiczne `not`, `or`, `and`
- operator wyłuskania wartości ze zmiennej "nullowalnej" `??`
- instrukcje warunkowe `if`, `elif`, `else`
- pętla `while`
- obsługa funkcji nazwanych oraz anonimowych (lambd) - definicje, wywołania
- funkcję można przekazać jako argument do innych funkcji
- funkcja może zwracać inną funkcję
- możliwość dodawania komentarzy jedno i wieloliniowych

## Przykłady

### `const` vs `let`

```js
const var1: int;          // Error: Const value has to be initialized
let var1: int;            // Error: Variable has to be nullable
let var2: int = 2;        // this will work
var2 = 3;

const var3: int = 4;
var3 = 5;                 // Error: Cannot modify constant variable
```

### `nullable`

```js
/*
 variables can be uninstantiated
 both var1 and var2 will be null
*/
let var1
? : int;
let var2
? : int = null;
```

### `nullable` - dozwolone operacje

```js
let var3
? : int;

if (var3 == null) {
  const b: int = var3 * 10;   // Error: Unallowed operation for a nullable variable
} else {
  const a: int = var3 + 3;    // this will work
  print("Var3 nie jest nullem");
}
```

### `if` `elif` `else`, `while`

```js
let i: int = 0;

while (i <= 100) {
  if (i % 3 == 0 or
  i % 5 == 0
)
  {
    print("FizzBuzz");
  }

  elif(i % 3 == 0)
  {
    print("Fizz");
  }

  elif(i % 5 == 0)
  print("Buzz");    // shortened syntax for if, elif, else

else
  {
    print(i);
  }

  i = i + 1;
}
```

### `instrukcje zagnieżdżone`

```python
let
i: int = 0;

if (1 + 2 == 3) {
if (12 > 4) {
if (i == 0) {i = i + 1;}
else {
if (i != 1) {i = 1;}
}
}
elif (false) {i = i - 1;}
} else {
while (true) {
while (i != 3) {
return 2 > 3 + 1 != 10;}
}
}
```

### automatyczna konwersja między `int` a `float`, konkatencja `str` i `int`

```js
let num: float = (2.25 + (2 * 3) / 6 - 4) % 3; // This will work
const num1: int = 1 / 1 + 5 + 7 - 1.5; // Error: Explicit cast to float required

let a: str = "" + 3; // "3"
let b: int = 3 + "3"; // Error: Cannot concatenate type `int` with `str`
```

### deklaracja funkcji, zakres `globalny` i `lokalny`, wywołanie funkcji

```
let var1? : int;   // global scope

def
func()
:
void
=>
{
  return;
}

def
func0()
:
void
=>
{
}

def
func1(arg1
:
int, arg2
:
int
):
int => {
  const var1: str = "Hello";  // var1 is in a function scope so redeclaring variables should work
  return var1 + var2 + 3;
}

def
func2(arg1
:
int, arg2
:
int
):
func((arg3: int) => int)
=>
{
  return (arg3: int)
:
  int => {
    return arg1 + arg2 + arg3;
  }
}

def outer(): func(() => void) =>{
  const inner = ():void => {};
  return inner;
}

const b: func(() => void) = func0;
const result: int = func1(1, 2);
const fn: func((int) => int) = fun2(1, 2);
const res: int = fn(3); // 6
outer()();
```

### funkcje anonimowe, zwracanie innych funkcji, currying

```
// anonymous function returning another anonymous function

const adder = (offset: int): func((x: int, y: int) => int) => {
  return (x: int, y: int): int => {
    return offset + x + y;
  };
}
;

const add_with_offset: func = adder(2); // outer function
const sum_with_offset: int = add_with_offset(4, 5); // inner function
```

### równoważny zapis dla fukcji anonimowych

```
// lambda: syntax without return
const substract: func((x: int, y: int) => int) = (x: int, y: int): int => x - y;

// lambda: standard syntax
const substract: func((x: int, y: int) => int) = (x: int, y: int): int => {
  return x - y;
};

// downside of using shortened syntax with currying
const a = (x: int):func((int) => func((z: int) => int)) => (y: int):func((z: int) => int) => (z: int) => x + y + z;

// syntax can be mixed
const b: func((x: int) => func((y: int) => int)) = (x: int): func((y: int) => int) => {
  return (y: int): int => x + y;
}
```

### funkcje biblioteczne

`print(*args)`

---

## Gramatyka

```
Program = { ProgramStatement } ;

ProgramStatement = FuncDef | Statement ;

FuncDef = "def", Id, "(", Params ")", ":", ReturnType, "=>", FuncBody ;

LambdaDef = "(", Params ")", ":", ReturnType, "=>", FuncBody ; 

FuncBody = Body | Expr  ; # Expr == shorter syntax

Params = [ Param, { ",", Param } ] ;

Param = Id, DeclareTypeOp, VarType ;

Body = "{", { Statement }, "}" ;

Statement = Conditional 
        | Loop
        | Declaration
        | StatementShort
        | Body ;

StatementShort = Return | IdOperation ;

Loop = "while", "(", Expr, ")", Body ;

FuncCall = "(", Arguments, ")", { "(", Arguments, ")" } ;

Arguments = [ Expr, { ",", Expr } ] ;

Return = "return", [ Expr ], ";" ;

Conditional = "if", "(", Expr, ")", Statement, { ElifStatement }, [ "else", Statement ] ;

ElifStatement = "elif", "(", Expr, ")", Statement ;

Expr = NullCoalExpr, { "??" , NullCoalExpr } ;

NullCoalExpr = OrExpr, { "or", OrExpr } ;

OrExpr = AndExpr, { "and", AndExpr } ;

AndExpr = EqExpr, { EqOp, EqExpr } ;

EqExpr = CompFac, { CompOp, CompFac } ;

CompFac = ["not"], AddFac ;

AddFac = MultFac, { AddOp, MultFac } ;

MultFac = Factor, { MultOp, Factor } ;

Factor = (["-"], Literal)
        | Id, [ FuncCall ]
        | "(", [ Expr ] , ")" ;

Literal = Number | String | Boolean | Null ;

IdOperation = Id, ( Assignment | FuncCall ), ";" ;

Assignment = "=", Expr ;

Declaration = DeclareKeyword, Id, DeclareTypeOp, VarType, "=", Expr, ";" ;

DeclareKeyword = "const" | "let" ;

DeclareTypeOp = "?:" | ":" ;

AddOp = "+" | "-" ;

MultOp = "*" | "/" | "%" ;

EqOp = "==" | "!=" ;

CompOp = "<" | "<=" | ">" | ">=" ;

VarType = "str"
        | "int"
        | "float"
        | "bool"
        | FuncType ;

FuncType = "func", "(", "(", Params, ")", "=>", ReturnType, ")" ;

ReturnType = VarType | "void" ;

String = "\"", {all utf-8 chars}, "\""
       | "\'", {all utf-8 chars}, "\'" ;

Number = Integer, [".", { Integer }]

Integer = Digit, { Digit } ;

Boolean = "true" | "false" ;

Null = "null" ;

Id = Letter, { Letter | Digit } ;

Letter = "a" .. "Z"
        | "A" .. "Z"
        | "_" ;

Digit = "0" .. "9" ;
```

```
Comment = "/", "/", {all utf-8 chars}, "\n" ;
MultilineComment = "/", "*", {all utf-8 chars except "*" | "\n"}, "*", "/" ;
```

---

## Wymagania funkcjonalne i niefunkcjonalne

### Wymagania funkcjonalne

- wejście programu: ścieżka do pliku do zinterpretowania podawana jako argument linii poleceń
- obsługa źródła tekstowego na potrzeby testów jednostkowych
- wyjście języka: standardowy strumień wyjścia
- brak `hoistungu` zmiennych i funkcji (wymagana wcześniejsza deklaracja)

### Wymagania niefunkcjonalne

- program napisany w języku Python
- program nie powinien kończyć się nie obsłużonym wyjątkiem
- wysokie pokrycie kodu testami

## Obsługa błędów

- każdy moduł będzie posiadał swoją własną klasę wyjątków, która będzie dziedziczyła po klasie
  bazowej `Error(Exception)`.

## Opis testowania

Do testowania zostanie wykorzystany moduł `unittest` z biblioteki standardowej oraz zewnętrzna paczka `coverage` do
pomiaru pokrycia kodu testami.

Przeprowadzone zostaną:

- testy jednostkowe - sprawdzanie przypadków częstych, skrajnych, złośliwych
- testy integracyjne sprawdzające wspólne działanie modułów (m.in Lexer + Parser)

## Sposób uruchomienia

Do uruchomienia programu wymagany jest Python w wersji minimum 3.8

```shell
python cli.py -f <path_to_file>
```


# TODO
- poprawić przykłady
- krótszy syntax dla lambd i (funkcji) -- OPCJONALNIE
- krótszy syntax dla while/if itd. -- OPCJONALNIE