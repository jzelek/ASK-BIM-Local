# **ASK-BIM Tool Evaluation on Barcelona.ifc**

### **Overview**
The following results come from testing the **ASK-BIM tool** on the **Barcelona.ifc** file, which was converted into an **LBD (Linked Building Data) graph** using the **IFC-to-LBD converter**. The evaluation categorizes questions based on their complexity and reasoning type, analyzing whether the tool can correctly answer them given the graph's structure. 

Each question is classified as:
- **(D)** = **Direct Question** (Answerable using explicitly represented entities and properties in the graph).  
- **(I)** = **Indirect Question** (Requires additional reasoning, inference, or aggregation beyond directly stored data).  

Additionally, each question is evaluated for correctness:
- ✅ **Correct** = The provided answer fully addressed the question.  
- ⚠️ **Partially Correct** = the response contained minor errors or missing details.  
- ❌ **Incorrect** = The system failed to generate a valid or meaningful answer.  

---

## **Single Entity, Single Property**
1. ✅ **(D)** How many doors are there on the second floor of the building?  
2. ✅ **(D)** What is the size of the smallest window in the building?  
3. ✅ **(D)** What is the total number of treads in the building?  
4. ✅ **(D)** What is the height of the tallest column in the building?  
5. ❌ **(I)** How many rooms are located on the second floor?  
6. ✅ **(D)** Which storey has the highest number of doors?  
7. ⚠️ **(I)** What is the average ceiling height of all hallways in the building?  

---

## **Single Entity, Multiple Properties**
1. ✅ **(D)** What is the total surface area of all the walls on the second floor?  
2. ✅ **(D)** What is the highest riser on the stairs of the building?  
3. ✅ **(D)** Can you generate a detailed description of a window in the building using all its available properties and values?  
4. ✅ **(D)** Which properties of windows 

