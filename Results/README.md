# **Tool Evaluation on Barcelona.ifc**

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
4. ✅ **(D)** Which properties of windows are related to their orientation or position in the building?  
5. ✅ **(D)** What is the fire rating of the largest door in the building?  
6. ✅ **(D)** Which walls on the ground floor are classified as load-bearing and have a height greater than 3 meters?  
7. ⚠️ **(I)** What is the total glazed area of windows on the second floor?  

---

## **Based on Reasoning**
1. ✅ **(D)** Which windows are installed on walls with a height greater than 3 meters?  
2. ✅ **(D)** What is the biggest size window that I could fit in the smallest wall?  
3. ❌ **(I)** The number of windows in the building can be considered reasonable?  
4. ❌ **(I)** What is the total structural load supported by load-bearing walls on each floor?  
5. ✅ **(D)** Which walls are supporting other structural elements in the building?  
6. ❌ **(I)** What is the total area enclosed by the walls on the second floor?  
7. ✅ **(D)** What is the window-to-wall ratio in the building?  
8. ✅ **(D)** Which columns span across multiple floors in the building?  
9. ❌ **(I)** What is the ratio of usable floor area to the gross area for the second floor?  
10. ❌ **(I)** Which ramps in the building are accessible according to universal design standards?  
11. ❌ **(I)** Are there any irregular-shaped rooms?  
12. ❌ **(I)** Which corridors have doors wider than 900mm?  
13. ❌ **(I)** How many windows are in each of the facades?  

---

### **Conclusion**
The ASK-BIM tool was tested on a **structured IFC dataset** converted into **Linked Building Data (LBD)** format. This classification provides insights into which questions can be **fully answered, partially answered, or not supported** due to limitations in the **graph representation or the tool’s reasoning capabilities** or in the tool capabilities.

Further refinements to the **LBD conversion process** and **querying mechanisms** could improve the ability of the tool to handle more complex reasoning tasks.
