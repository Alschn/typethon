# TKOM - Interpreter języka `Typethon`

## Opis

Typethon to wymyślony język przypominający składnią języki Python i Typescript. Pozwala na definiowanie zmiennych
mutowalnych, niemutowalnych, a także "nullowalnych". Obsługuje funkcje anonimowe (wyrażenia lambda).

## Założenia

- język **silnie** i **statycznie** **typowany**
- obsługuje typy danych: `int`, `float`, `str`, `bool`, `func`
- obsługuje "nullowalność" zmiennych (`?:` zamiast `:` przy deklaracji typu) oraz specjalną wartość `null`
- zmienne mogą być mutowalne lub niemutowalne - `let` vs `const`
- operatory arytmetyczne `+`, `-`, `*`, `/`, `%`, `>`, `>=`, `<`, `<=`, `==`, `!=`
- operatory logiczne `not`, `or`, `and`
- operator wyłuskania wartości ze zmiennej "nullowalnej" `??`
- instrukcje warunkowe `if`, `elif`, `else`
- pętla `while`
- obsługa funkcji nazwanych oraz anonimowych (lambd) - definicje, wywołania
- funkcję/wyrażenie lambda można przekazać jako argument do innych funkcji
- funkcja zwraca jedną wartość
- funkcja może zwracać inną funkcję
- możliwość dodawania komentarzy jedno i wieloliniowych

## Zdefiniowane zachowania:

### Operatory:

#### Operator `+`

#### Operator `-`

#### Operator `*`

#### Operator `/`

#### Operator `%`

#### Operator `not`

#### Operatory `and` i `or`

#### Operatory `>`, `>=`, `<`, `<=`

#### Operatory `==`, `!=`


## Przykłady

### `const` vs `let`

```
const var1: int;          // Error: Const value has to be initialized
let var1: int;            // Error: Variable has to be nullable
let var2: int = 2;        // this will work
var2 = 3;

const var3: int = 4;
var3 = 5;                 // Error: Cannot modify constant variable
```

### `nullable`

```
/*
 variables can be uninstantiated
 both var1 and var2 will be null
*/

let var1? : int;
let var2? : int = null;
```

### `nullable` - dozwolone operacje

```
let var3? : int;

if (var3 == null) {
  const b: int = var3 * 10;   // Error: Unallowed operation for a nullable variable
} else {
  const a: int = var3 + 3;    // this will work
  print("Var3 nie jest nullem");
}
```

### `if` `elif` `else`, `while`

```
let i: int = 0;

while (i <= 100) {
  if (i % 3 == 0 or i % 5 == 0) {
    print("FizzBuzz");
  }

  elif(i % 3 == 0) {
    print("Fizz");
  }

  elif(i % 5 == 0) print("Buzz");    // shortened syntax for if, elif, else

  else {
      print(i);
  }
  
  i = i + 1;
}
```

### `instrukcje zagnieżdżone`

```
let i: int = 0;

if (1 + 2 == 3) {
  if (12 > 4) {
    if (i == 0) {
      i = i + 1;
    }
    else {
      if (i != 1) {i = 1;}
    }
  }
  elif (false) {
    i = i - 1;
  }
  } else {
    while (true) {
      while (i != 3) {
        return 2 > 3 + 1 != 10;
      }
    }
}
```

### automatyczna konwersja między `int` a `float`, konkatencja `str` i `int`

```
let num: float = (2.25 + (2 * 3) / 6 - 4) % 3;  // This will work
const num1: int = 1 / 1 + 5 + 7 - 1.5;          // Error: Explicit cast to float required

let a: str = "" + 3;                            // "3"
let b: int = 3 + "3";                           // Error: Cannot concatenate type `int` with `str`
```

### deklaracja funkcji, zakres `globalny` i `lokalny`, (wielokrotne) wywołanie funkcji

```
let var1? : int;   // global scope

def func(): void => {
  return;
}

def func0(): void => {

}

def func1(arg1: int, arg2: int): int => {
  const var1: str = "Hello";  // var1 is in a function scope so redeclaring variables should work
  return var1 + var2 + 3;
}

def func2(arg1: int, arg2: int): func((arg3: int) => int) => {
  return (arg3: int): int => {
    return arg1 + arg2 + arg3;
  };
}

def outer(): func(() => void) => {
  const inner: func(() => void) = (): void => {};
  return inner;
}


const b: func(() => void) = func0;
const result: int = func1(1, 2);
const fn: func((a: int) => int) = fun2(1, 2);
const res: int = fn(3); // 6

outer()();
b();
```

### funkcje anonimowe, zwracanie innych funkcji

```
// anonymous function returning another anonymous function
const adder: func((offset: int) => func((x: int, y: int) => int)) = (offset: int): func((x: int, y: int) => int) => {
  return (x: int, y: int): int => {
    return offset + x + y;
  };
};


const add_with_offset: func() = adder(2); // outer function       # TODO
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
// this is a valid construction
const a: int = (x: int): func((x: int) => func((y: int) => func((z: int) => int))) => (y: int): func((z: int) => int) => (z: int): int => x + y + z;

// syntax can be mixed
const b: func((x: int) => func((y: int) => int)) = (x: int): func((y: int) => int) => {
  return (y: int): int => x + y;
};
```

### funkcje biblioteczne

`print(*args)` - przyjmuje wiele argumentów o dowolnym typach
`String()`
`Integer()`
`Float()`
`Boolean()`
``

---

## Gramatyka

```
Program = { ProgramStatement } ;

ProgramStatement = FuncDef | Statement ;

FuncDef = "def", Id, "(", Params ")", ":", ReturnType, "=>", FuncBody ;

FuncBody = Body | Expr ;

Params = [ Param, { ",", Param } ] ;

Param = Id, DeclareTypeOp, VarType ;

Body = "{", { Statement }, "}" ;

Statement = Conditional 
        | Loop
        | Declaration
        | Return
        | IdOperation
        | Body ;

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

MultFac = NegFac, { MultOp, NegFac } ;

NegFac = ["-"], Factor ;

Factor =  Literal
        | Id, [ FuncCall | RestOfLambdaDef]
        | "(", [ Expr ] , ")"  ;

RestOfLambdaDef = DeclareTypeOp, VarType, { ",", Param }

Literal = Number | String | Boolean | Null ;

IdOperation = Id, ( Assignment | FuncCall ), ";" ;

Assignment = "=", Expr ;

Declaration = DeclareKeyword, Id, DeclareTypeOp, VarType, ["=", Expr] , ";" ;

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

Do uruchomienia programu wymagany jest Python w wersji minimum 3.10 (ze względu na użycie wyrażeń match case).

```shell
python cli.py -f <path_to_file>
```

Uruchomienie testów jednostkowych
```
coverage run unittest -m discover
```

Raport z uruchomienia testów jednostkowych z informacją o m.in pokryciu kodu testami
```
coverage report -m
```
