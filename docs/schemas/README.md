# What is JumpScale Schema

According to wikipedia *"The word schema comes from the Greek word σχήμα (skhēma), which means shape, or more generally,
 plan"*.  
In databases "Schema" is some files or some structured code describing the tables and it's fields and data types of each
 field.  

JumpScale Schema is a way to define an efficient but yet powerful schemas for your data, Taking advantage of 
[capnp's]('https://capnproto.org/language.html') high performance and readability of 
[TOML Lang]("https://github.com/toml-lang/toml") combining it with complex data types to achieve both 
usability and high performance.

# What do you need to know to define a new schema

## Schema url

The very first part of the schema is the url, Each schema should have it's unique url over the application.
you can define the schema url like that.  

```toml
@url = schema.test
```

## Data types

see [schemas/readme.md]


### Complex data types

you can define more complex data types by nesting schemas  

Example:

```toml
@url = schema.address
street = (S)
floor = (I)
apartment = (I)
```

```toml
@url = schema.student
name = (S)
subjects = (LS)
address = (O) !schema.address
```

### How to use schema 

```
schema = """
        @url = despiegk.test
        llist2 = "" (LS) #L means = list, S=String        
        nr = 4
        date_start = 0 (D)
        description = ""
        token_price = "10 USD" (N)
        llist = "1,2,3" (LI)
        llist1 = "1,2,3" (L)
        """
```

## to get schema from schema_text

```python
schema_test = j.data.schema.get(schema_text_path=schema)
schema_object = schema_test.get()
```

## to add data using schema

```python
schema_object.token_price = "20 USD"
schema_object.llist.append(1)
schema_object.description = "something"
```

- for a full example of using schema see the following [test link](data/schema/tests)

## Schema Test

### run all tests

```python
kosmos 'j.data.schema.test()'
```

### run specific test

```python
kosmos 'j.data.schema.test(name="base")'
kosmos 'j.data.schema.test(name="capnp_schema")'
kosmos 'j.data.schema.test(name="embedded_schema")'
kosmos 'j.data.schema.test(name="lists")'
kosmos 'j.data.schema.test(name="load_data")'
```

TODO: list not complete

TODO: there is duplication with below, lets fix


# jumpscale schemas

## format of the schema


```python
@url = despiegk.test.1
llist2 = "" (LS) #L means = list, S=String        
nr = 4
date_start = 0 (D)
description = ""
token_price = "10 USD" (N)
cost_estimate:hw_cost = 0.0 #this is a comment
llist = []
llist3 = "1,2,3" (LF)
llist4 = "1,2,3" (L)
llist5 = "1,2,3" (LI)
U = 0.0
pool_type = "managed,unmanaged" (E)
```

- @url is the unique locator of the schema, try to have this unique on global basis
  - its good practice to put an version nr at the end of the url

### simple types

- I
  - Integer
- F:
  - Float
- N:
  - Numeric, has support for currencies
  - can e.g. insert 10 EUR, 10 USD, 10k USD
- S:
  - string
- B:
  - boolean
  - true,True,1 are all considered to be True

```python
type is one of following
- s, str, string
- i, int, integer
- f, float
- b, bool,boolean
- tel, mobile
- d, date
- n, numeric
- h, hash       #set of 2 int
- p, percent
- o, jsobject
- ipaddr, ipaddress
- ipport, tcpport
- iprange
- email
- multiline
- list
- dict
- yaml
- set
- guid
- url, u
- e,enum        #enumeration
```
for full list see j.data.types

### collection types

- L
- e.g. LI is list of integer

#### collection of other objects

```python
@url =  jumpscale.digitalme.package
name = "UNKNOWN" (S)           #official name of the package, there can be no overlap (can be dot notation)
enable = true (B)
args = (LO) !jumpscale.digitalme.package.arg
loaders= (LO) !jumpscale.digitalme.package.loader

@url =  jumpscale.digitalme.package.arg
key = "" (S)
val =  "" (S)

@url =  jumpscale.digitalme.package.loader
giturl =  "" (S)
dest =  "" (S)
enable = true (B)
```

- generic format ```(LO) !URL```

### defaults

- ```enable = true (B)```
    - in this case the default is true, so basically everything in between = and (
- ```name = myname (S)``` or ```name = myname```
    - if type not specified the schemas will try to guess the type e.g. Int, String, ...

## how to get a new schema

```python
def get(self, schema_text="", url=None, die=True):
    """
    get schema from the url or schema_text

    Keyword Arguments:
        schema_text {str} -- schema file path or shcema string  (default: {""})
        url {[type]} -- url of your schema e.g. @url = despiegk.test  (default: {None})
        
    if die False and schema is not found e.g. based on url, then will return None

    Returns:
        Schema
    """
    ...

SCHEMA="""
@url =  jumpscale.digitalme.package.1
name = "UNKNOWN" (S)           #official name of the package, there can be no overlap (can be dot notation)
abool = true (B)
"""

s=j.data.schema.get(SCHEMA)

#if the schema already exists then can do
s=j.data.schema.get(url="jumpscale.digitalme.package.1") #will die if not exists


```

## how to get a new object

```python
s=j.data.schema.get(url="jumpscale.digitalme.package") #will die if not exists
obj = s.new()
obj.abool = True
obj.abool = 1
assert obj.abool == True
obj.abool = 0
assert obj.abool == False
```

can see how the type system we use is intelligent, especially if used for things like numerics.


### enumerators

- are cool, you can store long string representations and they will only take 4 bytes to store (int)

e.g.

```
schema = """
    @url = despiegk.test2
    enum = "red,green,blue" (E) #first one specified is the default one
    """
s=j.data.schema.get(schema_text=schema)
o=s.new()
assert o.enum == "RED" 
o.enum = 3
assert o.enum == 'RED'  #is always sorted on alfabet

```
