# **Tox Programming Language**

```Tox``` is a small programming language designed to run on a Virtual Machine. The Virtual Machine executable is located in ```vm/```. This programming language was built using the library [ply](www.dabeaz.com/ply/). 

**Note**: The Virtual Machine was developed by students at the University of Minho, Portugal.I did not develop the Virtual Machine, I only developed the programming language. To learn more about the Virtual Machine, please refer to the zip file ```vms-vf.zip``` in the ```vm/``` directory. Also note that I made some modifications to the Virtual Machine in order to make it compatible with the Virtual Machine at [EWVM](https://ewvm.epl.di.uminho.pt/). Those modifications include:
- Adding a new instructions to the Virtual Machine (```AND```, ```OR```).
- Improving the memory consumption of the Virtual Machine by reducing the number of memory leaks.

## **Installation**

Installing through pip:

```console
git clone https://github.com/fabiocfabini/tox.git
cd tox
make install
pip install -e .
```

**Note**: Only works on linux.

## **Quick Start**

```console
tox run examples/hello_world.tox
```

## **Features**

### **Comments**

To add one line comments, simply type ```//``` followed by the comment. For example:

```c
// This is a comment
```

Multiline comments can be added by typing ```/*``` followed by the comment and ```*/``` at the end. For example:

```c
/*
This is a multiline comment
*/
```

### **Data Types**

Has of now, the language supports the following data types:

- ```int```: 32 bit integer;
- ```&int```: array of 32 bit integers;
- ```string```: Unmutable strings;

### **Arithmetics**

Basic arithmetics are supported by the language. These include:

- the ```+```, ```-```, ```*```, ```/``` operators;
- the ```==```, ```!=```, ```<```, ```>```, ```<=```, ```>=``` operators;
- the ```&&```, ```||``` operators;
- the ```!``` operator;

**Note** Pointer arithmetics is not supported yet. [todo#3](todo.md)

### **Variables**

To declare a variable, simply type the variable name followed by ```:``` and the variable type. For example:

```c
a: int
```

Variables declared in this way are initialized with the value ```0```. To declare a variable and initialize it with a value, simply type the variable name followed by ```:``` and the variable type followed by ```=``` and the value. For example:

```c
a: int = 10
```

To modify the value of a variable, simply type the variable name followed by ```=``` and the value. For example:

```c
a = 20
```

### **Arrays**

In tox arrays are declared in 3 different ways:

- Declaring an array of a specific size. This will initialize the array with the value ```0```;

```c
a: &int[10]
```

- Declaring an array through a list of values;

```c
a: &int = [10, 20, 30, 40, 50]
```

- Declaring an array with the ```...``` operator;

```c
a: &int = [1 ... 10]
```

This will initialize the array with the values ```1, 2, 3, 4, 5, 6, 7, 8, 9, 10```.

To access an array element, simply type the array name followed by ```[``` and the index of the element followed by ```]```. For example:

```c
a[0]
```


### **Control Flow**

The control flow of the language is similar to the control flow of C. These include:

- ```if```, ```if else``` and ```if else if``` statements;

```c
if expression {
    // code
}

// or

if expression {
    // code
} else {
    // code
}

// or

if expression {
    // code
} else if expression {
    // code
} else {
    // code
}
```

- ```while``` statements;

```c
while expression {
    // code
}
```

- ```do while``` statements;

```c
do {
    // code
} while(expression)
```

- ```for``` statements;

```c
for(i: int = 0; i < 10; i = i + 1) {
    // code
}
```


### **Functions**

To declare a function start with the key word ```func``` followed by the function name, the function parameters and the function return type. For example:

```c
func sum(a: int, b: int) -> int {
    return a + b
}
```

To call a function, simply type the function name followed by the function parameters. For example:

```c
sum(10, 20)
```
