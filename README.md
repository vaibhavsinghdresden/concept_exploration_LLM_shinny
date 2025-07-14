# LLM-Enhanced Formal Concept Analysis: A Novel Approach to Semantic Mapping and Knowledge Discovery
This project is currently under active development and is being supervised by [Dr. Sergei Obiedkov](https://iccl.inf.tu-dresden.de/web/Sergei_Obiedkov/en)

## 1. Background: Formal Concept Analysis (FCA)

**Formal Concept Analysis (FCA)** is a mathematical framework for data analysis that focuses on identifying and visualizing relationships between a set of **objects** and a set of **attributes**. Developed by Rudolf Wille in the early 1980s, FCA is grounded in **lattice theory** and is widely used in knowledge representation, data mining, and ontology engineering.

### 1.1 Formal Context

Think of this as a simple table showing "what has what" - like a spreadsheet where rows are objects, columns are attributes, and checkmarks shows that this specific attribute is present in that object.

formally, A **formal context** in FCA is a triple: 

K = (G, M, I)

Where:
- **G** is a set of **objects**
- **M** is a set of **attributes**
- **I** is a binary relation (subset of G × M) indicating which object has which attribute  
  (i.e., (g, m) ∈ I means object *g* has attribute *m*)

For example concider the below formal concept which represents a small set of **person categories** based on their **gender** and **age group**.:

|        Object        | Female | Male | Juvenile | Adult |
|:--------------------:|:------:|:----:|:--------:|:-----:|
| **girl**             |   ✔️   |      |    ✔️    |       |
| **woman**            |   ✔️   |      |          |  ✔️   |
| **boy**              |        |  ✔️  |    ✔️    |       |
| **man**              |        |  ✔️  |          |  ✔️   |

^Taken from [upriss.github.io](https://upriss.github.io/fca/fcaintro.html)

In this context the **Objects** are `girl`, `woman`, `boy`, `man` and the **Attributes** are `female`, `male`, `juvenile`, `adult`. Each object is described by the attributes that apply to it, like A **girl** is **female** and **juvenile**

This setup defines a simple logical structure where each object can be classified by its gender and age. It allows us to explore patterns and relationships—like grouping all **juveniles**, all **females**, or all **adults**—based on shared attributes.


### 1.2 Formal Concepts

A **formal concept** is a pair:

(A, B)

Where:
- **A** ⊆ G is the **extent** (the set of objects sharing the attributes in B)
- **B** ⊆ M is the **intent** (the set of attributes common to all objects in A)

These satisfy the following conditions:

A = { g ∈ G | ∀ m ∈ B: (g, m) ∈ I }

B = { m ∈ M | ∀ g ∈ A: (g, m) ∈ I }

From our context, below are some formal concepts can be derived:

1. **({girl}, {female, juvenile})**  
2. **({woman}, {female, adult})**  
3. **({boy}, {male, juvenile})**  
4. **({man}, {male, adult})**  

These concepts form the building blocks of the **concept lattice**, which organizes them hierarchically based on shared attributes and object groupings.

These formal concepts form a **concept lattice**, which reveals hierarchical relationships among concepts.

For our example we get the below lattice daigram

<img width="296" height="246" alt="Screenshot 2025-07-14 at 11 14 11 PM" src="https://github.com/user-attachments/assets/275c7df2-b9b0-4909-87fa-ac709e3ca703" />

### 1.3 Attribute Implications

An **attribute implication** is a rule of the form:

X → Y

Where X, Y ⊆ M. This means:

> If an object has all the attributes in set X, then it also has all the attributes in set Y.

These implications capture dependencies between attributes and can be used for reasoning and data compression. FCA provides tools to compute a minimal (canonical) set of such implications, known as the **Duquenne–Guigues basis**.


### 1.4 Object Implications

**Object implications** are less commonly used and arise in the **dual** setting of FCA:

A → B

Where A, B ⊆ G. This means:

> If all objects in A share certain attributes, then the same holds for objects in B.

While analogous to attribute implications, object implications are mainly explored in theoretical extensions of FCA.







