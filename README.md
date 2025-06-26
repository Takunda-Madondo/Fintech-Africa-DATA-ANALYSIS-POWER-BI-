# Fintech Usage Analysis – POWER BI and DAX

## Overview
This Power BI dashboard analyzes fintech adoption and user behavior across African markets. It provides insights into usage patterns, barriers to adoption, and opportunities for strategic expansion. The dashboard consists of four main pages:

---

## 📄 **Page 1: Overview & Key Metrics**

**Objective:** Provide a general snapshot of fintech usage.

**Key KPIs:**
- Total Users
- Active Users
- Average Transaction Value / Month
- Fintech Adoption Rate
- Active Countries

**Visuals:**
- KPI cards
- Country Map
- Line chart: adoption rate by year
- Pie Chat: Usage by Gender
- Bar Chat: Usage by coutry
  
**Slicers**
 - Year
 - Country

---

## 📄 **Page 2: Demographics & Usage Patterns**

**Objective:** Explore fintech usage across age groups, gender, urban/rural split, and phone types.

**Key KPIs:**
- Female users percentage
- Total Users
- Urban users percentage
- Dorminant age range

**Visuals:**
- Clustered bar chat: users by age and gender
- Pie chat: users by phonetype
- Donut Chat: Users by Location

 **Slicers**
 - Year
 - Country

---

## 📄 **Page 3: Use Case & Barrier Analysis**

**Objective:** Analyze specific use cases and barriers faced by users.

**Key KPIs:**
1. **Most Common Use Case**
2. **Total Use Cases**
3. **% of Users using multiple Use Cases**

**Visuals:**
- Clustered Column chat: Use case by country -legend : Use case
- Line Chat: Monthly transaction value by gender and use case
- Matrix: Use Case Barries

**Slicers**
 - Age Group
 - Gender
 - Year

---

## 📄 **Page 4: Strategic Insights and Adoption Gaps**

**Key KPIs:**
1. **Top 3 Use Cases**
2. **%Users Using Multiple Use cases**
3. **Top 3 barriers**

---
**Key DAX Functions:**

### Replace Null Use_Cases with "Unknown" or desired value:

```dax
UnifiedUseCases =
ADDCOLUMNS(
    FILTER(
        GENERATE(
            VALUES(MainTable[User_ID]),
            { (MainTable[Use_Case_1]), (MainTable[Use_Case_2]) }
        ),
        NOT ISBLANK([Value])
    ),
    "Use_Case", COALESCE([Value], "Unknown")
)
```
## DISTINCT COUNT: 
```dax
DistinctUseCaseCount = DISTINCTCOUNT(UnifiedUseCases[Use_Case]
```
## % OF MULTI USERS:
```dax
MultiUseUserPercent = 
VAR UserCaseTable =
    ADDCOLUMNS(
        VALUES(UnifiedUseCases[User_ID]),
        "UseCaseCount", CALCULATE(DISTINCTCOUNT(UnifiedUseCases[Use_Case]))
    )
VAR MultiUsers = COUNTROWS(FILTER(UserCaseTable, [UseCaseCount] > 1))
VAR TotalUsers = DISTINCTCOUNT(UnifiedUseCases[User_ID])
RETURN DIVIDE(MultiUsers, TotalUsers)
```

## TOP 3 USE CASES:
```dax
TopUseCase_1 = 
MAXX(
    TOPN(1,
        SUMMARIZE(UnifiedUseCases, UnifiedUseCases[Use_Case], "UserCount", DISTINCTCOUNT(UnifiedUseCases[User_ID])),
        [UserCount], DESC
    ), [Use_Case]
)
```

## TOP 3 BARRIERS:
```dax
TopBarrier_1 = 
MAXX(
    TOPN(1,
        SUMMARIZE(UnifiedUseCases, UnifiedUseCases[Barrier], "UserCount", DISTINCTCOUNT(UnifiedUseCases[User_ID])),
        [UserCount], DESC
    ), [Barrier]
)

```
---

**📌 Project Conclusion**

This project demonstrates strong proficiency in end-to-end data analysis using Power BI and DAX.
From data cleaning and transformation to KPI design, interactive visual storytelling, and custom DAX logic,
the dashboard reflects the ability to translate raw data into actionable business intelligence. 
Techniques applied such as building virtual tables, implementing advanced filters, calculating dynamic ranks, 
and optimizing for mobile, showcase a comprehensive skill set in data modeling, analytical thinking, and stakeholder-focused reporting.
