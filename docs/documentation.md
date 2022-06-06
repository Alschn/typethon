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
- operator wyłuskania wartości ze zmiennej `??`
- instrukcje warunkowe `if`, `elif`, `else`
- pętla `while`
- obsługa funkcji nazwanych oraz anonimowych (lambd) - definicje, wywołania
- funkcję/wyrażenie lambda można przekazać jako argument do innych funkcji
- funkcja zwraca jedną wartość
- funkcja może zwracać inną funkcję
- możliwość dodawania komentarzy jedno i wieloliniowych

## Zdefiniowane zachowania:

### Zmienne
- przypisanie wartości typu Null do zmiennej nienullowalnej powoduje rzucenie wyjątku
- globalną zmienną można nadpisać o ile nie jest `const`
- zmienna oznaczona przez `const` jest niemutowalna i próba jej modyfikacji poskutkuje rzuceniem wyjątku
- można odwoływać się do zmiennych z wyższych `scope`ów
- zmienną można wywołać, jeśli jest typu Func.
- można rzutować zmienną na inny typ, jednak nie dla każdego typu rzutowanie ma sens

### Funkcje
- wymagana jest zgodność typów argumentów i typu zwracanego w czasie wykonania funkcji
(w przeciwnym wypadku rzucenie wyjątku przy próbie wywołania funkcji) - 
- typy funkcji są zgodne wtedy i tylko wtedy gdy zgadzają się typy argumentów i typ zwracany
- **argumenty przekazywane przez wartość**
- funkcja anonimowa może być przekazana jako argument, również przez **wartość**
- rekurencyjne wywołania są dozwolone
- funkcja może zwracać jedną wartość, inną funkcję (dowolna ilość zagnieżdżeń)

### Operatory:

#### Operator `+`
- dla typów Integer, Float dodaje wartości numeryczne
- dla typów String konkatenuje napisy
- dla innych błąd

#### Operator `-`
- dla typów Integer, Float odejmuje wartości numeryczne
- dla innych błąd

#### Operator `*`
- dla typów Integer, Float wykonuje mnożenie wartości numerycznych
- dla innych błąd

#### Operator `/`
- dla typów Integer, Float wykonuje dzielenie wartości numerycznych
- dla innych błąd
- dzielenie przez zero skutuje rzuceniem wyjątku

#### Operator `%`
- dla typów Integer, Float wykonuje dzielenie z resztą wartości numerycznych
- dla innych błąd
- dzielenie przez zero skutuje rzuceniem wyjątku

#### Operator `not`
- zdefiniowany dla typu Bool
- dla innych typów błąd

#### Operatory `and` i `or`
- zdefiniowane dla typów Bool
- dla innych typów błąd

#### Operatory `>`, `>=`, `<`, `<=`
- zdefiniowane dla typów Integer, Float
- dla innych typów błąd

#### Operatory `==`, `!=`
- zdefiniowany dla typu Bool, Integer, Float, String
- dla innych typów błąd

#### Operator `??`
- zwraca lewą stronę wyrażenia, jeśli nie jest typu Null
- zwraca prawą stronę wyrażenia, jeśli lewa strona jest typu Null
- jeżeli obydwie strony są typu Null, zwraca prawą stronę


## Przykłady w języku Typethon:

### `const` vs `let`

```
const var1: int;          // UninitializedConstError: Missing initializer in const declaration of variable var1.
let var1: int;            // NotNullableError: Cannot assign null to variable var1 which is not nullable.

let var2: int = 2;        // this will work
var2 = 3;

const var3: int = 4;
var3 = 5;                 // ConstAssignmentError: Cannot assign to var3 because it is a constant.
```

### `nullable`

```
/* variables can be uninstantiated both var1 and var2 will be null */
let var1?: int;
let var2?: int = null;
```

### `nullable` - dozwolone operacje

```
let var3?: int;

if (var3 == null) {
  const b: int = var3 * 10;   // UnexpectedTypeError: Cannot multiply type Null with type Integer
}
```

```
let var?: int = 1;
var = null;
```

```
let var?: float = 0;
const value: float = var ?? 15;
print(value);               // 0 gets printed
```

```
let var?: str = null;
print(var ?? "Hello world!");  // "Hello world!" gets printed
```

### `if` `elif` `else`, `while`

```
let i: int = 0;

while (i <= 100) {                  // while does not support shortened syntax
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

### Instrukcje zagnieżdżone

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

### automatyczna konwersja w jedną stronę z `int` na `float`

```
let num: float = (2 + (2 * 3) - 4) % 3;  // This will work
const num1: int = 1 / 1 + 5 + 7 - 1.5;          // TypeMismatchError: Variable num1 was declared with type Integer but received type Float.
```

### operacje dozwolone tylko dla zgodnych typów 

```
let b: int = 3 + "3";                           // UnexpectedTypeError: Cannot add type Integer to type String
```

### deklaracja funkcji, zakres `globalny` i `lokalny`, (wielokrotne) wywołanie funkcji

```
let var1?: int;   // global scope

def func1(arg1: int, arg2: int): int => {
  const var1: int = 15;
  return var1 + arg1 + arg2;
}

def func2(arg1: int, arg2: int): func((arg3: int) => int) => {
  print(arg1, arg2);
  const arg: int = 0;
  return (arg3: int): int => {
    // unfortunately arg1, arg2 or other variables created in higher scope are not visible
    return 1 + arg3;
  };
}

def outer(): func(() => void) => {
  const inner: func(() => void) = (): void => {};
  return inner;
}

const result: int = func1(1, 2);

const fn: func((a: int) => int) = func2(1, 2);

const res: int = fn(3); // 4

print(res);
```

### równoważny zapis dla fukcji anonimowych

```
// lambda: syntax without return
const substract: func((x: int, y: int) => int) = (x: int, y: int): int => x - y;

// lambda: standard syntax
const substract2: func((x: int, y: int) => int) = (x: int, y: int): int => {
  return x - y;
};

// downside of using shortened syntax with currying
// this is a valid construction
const a: func((x: int) => func((x: int) => func((y: int) => func((z: int) => int)))) = (x: int): func((x: int) => func((y: int) => func((z: int) => int))) => (y: int): func((z: int) => int) => (z: int): int => x + y + z;

// syntax can be mixed
const b: func((x: int) => func((y: int) => int)) = (x: int): func((y: int) => int) => {
  return (y: int): int => x + y;
};

```

### funkcje biblioteczne

`print(*args)` - przyjmuje wiele argumentów o dowolnym typie, drukuje je na do konsoli, rzuca błąd dla typu Func  
`String()`     - rzutuje wartość innego typu na wartość typu String, rzuca błąd dla typu Func  
`Integer()`    - rzutuje wartość innego typu na wartość typu Integer,  
rzuca błąd dla typów innych niż Integer i Float, rzutowanie Floata na Integera skutkuje zaokrągleniem w dół
`Float()`      - rzutuje wartość innego typu na wartość typu Float, 
rzuca błąd dla typów innych niż Integer i Float  
`Boolean()`    - rzutuje wartość innego typu na wartość typu Bool, rzuca błąd dla typów innych niż Bool i Null,
wartość `null` rzutowana jest na `false`
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

- każdy moduł posiada swoją własną nadrzędną klasę wyjątków, która dziedziczy po klasie
  bazowej `Error(Exception)`. 
- uchwycenie któregoś ze zdefiniowanych wyjątków powoduje przerwanie wykonywania programu

## Opis testowania

Do testowania został wykorzystany moduł `unittest` z biblioteki standardowej oraz zewnętrzna paczka `coverage` do
pomiaru pokrycia kodu testami.

Przeprowadzone zostały:

- testy jednostkowe - sprawdzanie przypadków częstych, skrajnych, złośliwych
- testy integracyjne sprawdzające wspólne działanie modułów (Lexer + Parser)
- testy e2e - wykonanie programu przez interpreter

### Statystyki z testów:
- liczba przypadków testowych (uwzględniając testy parametryzowane): `562`
- pokrycie kodu testami: `94%`

---

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

---

## Co udało się zrealizować w ramach projektu

Zrealizowano wszystko oprócz:
- traktowania funkcji nazwanych jako zmienne (nie da się przypisać funkcji nazwanej do zmiennej)
- zakresów widoczności zmiennych wewnątrz lambd (w lambdzie można skorzystać tylko z zmiennych globalnych i argumentów)
