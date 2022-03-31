# TKOM - Interpreter języka `Typethon`

Typethon to wymyślony język przypominający składnią Pythona i Typescript. Pozwala na definiowanie zmiennych mutowalnych, niemutowalnych, a także "nullowalnych". Obsługuje funkcje anonimowe.

## Założenia

- język **silnie** i **statycznie** **typowany**
- obsługuje typy danych: `int`, `float`, `str`, `bool`, `func`
- obsługuje "nullowalność" zmiennych, operator `?:` oraz specjalną wartość `null`
- zmienne mutowalne lub niemutowalne - `const` vs `let`
- operatory arytmetyczne `+`, `-`, `*`, `/`, `%`, `>`, `>=`, `<`, `<=`, `==`, `!=`
- operatory logiczne `not`, `or`, `and`
- operator wyłuskania wartości ze zmiennej nullowalnej `??`
- oprócz zwykłych funkcji obsługiwane są również funkcje anonimowe (lambdy)
- funkcje można przekazywać jako argument do innych funkcji
- funkcja może zwracać inną funkcję

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
let var1?: int;           // this will work
let var2?: int = null;    // both var1 and var2 will be null
```

### `nullable` - dozwolone operacje

```js
let var3?: int;

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
    if (i % 3 == 0 or i % 5 == 0) {
        print("FizzBuzz");
    }

    elif (i % 3 == 0) {
        print("Fizz");
    }

    elif (i % 5 == 0) print("Buzz");    // shortened syntax for if, elif, else

    else {
        print(i);
    }

    i = i + 1;
}
```

### `instrukcje zagnieżdżone`

```python
let i: int = 0;

if (1 + 2 == 3) {
    if (12 > 4) {
        if (i == 0) i = i + 1;
        else {
            if (i != 1) i = 1;
        }
    }
    elif (false) i = i - 1;
} else {
    while (true) {
        while (i != 3) { i++; }
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

```js
let var1?: int;   // global scope

def func0(): void => {}

def func1(arg1: int, arg2: int): int => {
    const var1: str = "Hello";  // var1 is in a function scope so redeclaring variables should work
    return var1 + var2 + 3;
}

def func2(arg1: int, arg2: int): func((arg3: int) => int) => {
    return (arg3: int) => {
        return arg1 + arg2 + arg3;
    }
}

def outer(): func(() => void) => {
    const inner = () => {}
    return inner;
}

const b: func(() => void) = func0();
const result: int = func1(1, 2);
const fn: func((arg3: int) => int) = fun2(1, 2);
const res: int = fn(3); // 6
outer()();
```

### funkcje anonimowe, zwracanie innych funkcji (currying)

```js
// anonymous function returning another anonymous function
const adder = (offset: int): func((x: int, y: int) => int) => {
  return (x: int, y: int): int => {
    return offset + x + y;
  };
};

const add_with_offset: func = adder(2); // outer function
const sum_with_offset: int = add_with_offset(4, 5); // inner function
```

### równoważny zapis dla fukcji anonimowych

```js
// lambda: syntax without return
const substract = (x: int, y: int): int => x - y;

// lambda: standard syntax
const substract = (x: int, y: int): int => {
  return x - y;
};

// downside of using shortened syntax with currying
const a = (x: int): func((y: int) => func((z: int) => int)) => (y: int): func((z: int) => int) => (z: int) => x + y + z;

// syntax can be mixed
const b = (x: int) => {
    return (y: int) => x + y;
}
```

### funkcje biblioteczne

`print(arg)`  
`str(arg)`

---

## Gramatyka

```
Program = ProgramStatement, { ProgramStatement } ;

ProgramStatement = FuncDef | Statement ;

FuncDef = ["def", Id], "(", Args ")", ":", ReturnType, "=>", FuncBody ;

FuncBody = Body | ( Expression, [ ";" ] ) ;

Args = [ Arg, { ",", Arg } ] ;

Arg = Id, AssignOp, VarType ;

Body = "{", { Statement }, "}" ;

Statement = Conditional | Loop | StatementShort ;

StatementShort = Return | Assignment ;

Loop = "while", "(", Expression, ")", Body ;

Conditional = IfStatement, { ElifStatement }, [ "else", CondBody ] ;

IfStatement = "if", "(", Expression, ")", CondBody ;

ElifStatement = "elif", "(", Expression, ")", CondBody ;

CondBody = StatementShort | Body ;

FuncCall = "(", Arguments, ")" ;

Arguments = [ Expression, { ",", Expression } ] ;

Return = "return", Expression, ";" ;

Expression = SimpleExpression, [RelOp, SimpleExpression] ;

SimpleExpression = Sign, AddTerm, { AddOp, Sign, AddTerm } ;

AddTerm = MultTerm, { MultOp, MultTerm } ;

MultTerm = Literal
        | (Id, [ FuncCall ])
        | "(", Expression, ")"
        | FuncDef;

Literal = Number | String | Boolean | Null ;

Assignment = [ DeclareKeyword ], Id, [ DeclareTypeOp, VarType ], "=", Expression, ";" ;

DeclareKeyword = "const" | "let" ;

DeclareTypeOp = "?:" | ":" ;

AddOp = "+" | "-" | "or" ;

MultOp = "*" | "/" | "%" | "and" ;

RelOp = "<" | "<=" | ">" | ">=" | "==" | "!=" ;

VarType = str"
        | "int"
        | "float"
        | "bool"
        | FuncType ;

FuncType = "func", "(", "(", Args, ")", "=>", ReturnType, ")" ;

ReturnType = VarType | "void" ;

String = "\"", {all utf-8 chars}, "\""
       | "\'", {all utf-8 chars}, "\'" ;

Number = Sign, Integer, [".", { Integer }]

Integer = Digit, { Digit } ;

Boolean = "true" | "false" ;

Null = "null" ;

Id = Letter, { Letter | Digit } ;

Letter = "a" .. "Z"
        | "A" .. "Z"
        | "_" ;

Digit = "0" .. "9" ;

Sign = "-" | Empty ;

Comment = "/", "/", {all utf-8 chars}, Newline ;

MultilineComment = "/", "*", {all utf-8 chars except "*" | Newline}, "*", "/" ;

Newline = "\n" ;
Empty = "" ;
```

---

## Wymagania funkcjonalne i niefunkcjonalne

### Wymagania funkcjonalne

- interfejs konsolowy, ścieżka do pliku do zinterpretowania podawana jako argument
- obsługa źródła tekstowego na potrzeby testów jednostkowych
- ...

### Wymagania niefunkcjonalne

- interpreter napisany w języku Python
- program nie powinien kończyć się nie obsłużonym wyjątkiem
- ...

## Zwięzły opis sposobu realizacji modułów, tokeny, struktury danych

Source, Lexer, Parser, Interpreter...

## Obsługa błędów

- każdy moduł będzie posiadał swoją własną klasę wyjątków, która będzie dziedziczyła po klasie bazowej `Error(Exception)`.

## Opis testowania

Do testowania zostanie moduł `unittest` z biblioteki standardowej oraz zewnętrzna paczka `coverage` do pomiaru pokrycia kodu testami.

Przeprowadzone zostaną:

- testy jednostkowe - testowanie każdej metody, sprawdzanie przypadków częstych, skrajnych, złośliwych
- testy integracyjne sprawdzające wspólne działanie modułów (np. Lexer + Parser)

## Sposób uruchomienia

```shell
python cli.py -f <path_to_file>
```
