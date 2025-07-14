# LLM-Enhanced Formal Concept Analysis: A Novel Approach to Semantic Mapping and Knowledge Discovery
This project is currently under active development and is being supervised by [Dr. Sergei Obiedkov](https://iccl.inf.tu-dresden.de/web/Sergei_Obiedkov/en)

## Background: Formal Concept Analysis (FCA)

**Formal Concept Analysis (FCA)** is a mathematical framework for data analysis that focuses on identifying and visualizing relationships between a set of **objects** and a set of **attributes**. Developed by Rudolf Wille in the early 1980s, FCA is grounded in **lattice theory** and is widely used in knowledge representation, data mining, and ontology engineering.

### Formal Context

A **formal context** in FCA is a triple: 

K = (G, M, I)

Where:
- **G** is a set of **objects**
- **M** is a set of **attributes**
- **I** is a binary relation (subset of G × M) indicating which object has which attribute  
  (i.e., (g, m) ∈ I means object *g* has attribute *m*)

### Formal Concepts

A **formal concept** is a pair:

(A, B)


Where:
- **A** ⊆ G is the **extent** (the set of objects sharing the attributes in B)
- **B** ⊆ M is the **intent** (the set of attributes common to all objects in A)

These satisfy the following conditions:

A = { g ∈ G | ∀ m ∈ B: (g, m) ∈ I }
B = { m ∈ M | ∀ g ∈ A: (g, m) ∈ I }


Formal concepts form a **concept lattice**, which reveals hierarchical relationships among concepts.

Example: 
An example of a formal context and a concept lattice taken from [upriss.github.io](https://upriss.github.io/fca/fcaintro.html)

<img width="381" height="472" alt="Screenshot 2025-07-14 at 10 43 31 PM" src="https://github.com/user-attachments/assets/c29b985a-2bab-4c02-a48b-a16a6c0d7b7b" />



### Attribute Implications

An **attribute implication** is a rule of the form:






