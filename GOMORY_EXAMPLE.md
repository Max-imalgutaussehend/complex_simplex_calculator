# Gomory-Schnitte Beispiel

## Problem: Ganzzahlige Lösung für LP

### ANFANGSTABLEAU (mit Schlupfvariablen s_1, s_2 in Basis)

**Objective:**
```
x_1 + x_2
```

**Constraints:**
```
2*x_1 + x_2 <= 4, x_1 + 2*x_2 <= 4
```

**Objective Type:** max

**Erwartetes Ergebnis:**
- Initial: Z = 0, Basis = [s_1, s_2], x_1=0, x_2=0
- Nach Simplex: Z = 2.6667, Basis = [x_1, x_2], x_1=1.333, x_2=1.333

---

### ENDTABLEAU (mit decision variables x_1, x_2 in Basis)

Dieses Tableau repräsentiert das **optimale** Tableau nach dem Simplex-Algorithmus.
Hier können dann Gomory-Schnitte hinzugefügt werden.

**Option 1: Über "Create New Tableau" Mode**

1. Wähle "Create New Tableau"
2. Number of Variables: 4 (x_1, x_2, s_1, s_2)
3. Number of Constraints: 2
4. Variable names: x_1, x_2, s_1, s_2

Tableau-Werte eingeben:
```
        x_1    x_2    s_1      s_2    RHS
Row 1:  1.0    0.0    0.6667  -0.3333  1.3333
Row 2:  0.0    1.0   -0.3333   0.6667  1.3333
z:      0.0    0.0    0.3333   0.3333  2.6667
```

Basis-Variablen:
- Row 1: x_1
- Row 2: x_2

**Option 2: Durch Constraints mit Konstanten (JETZT UNTERSTÜTZT!)**

**Objective:**
```
2.666667 - 0.333333*s_1 - 0.333333*s_2
```

**Constraints:**
```
1.333333 - 0.666667*s_1 + 0.333333*s_2 - x_1 >= 0,
1.333333 + 0.333333*s_1 - 0.666667*s_2 - x_2 >= 0
```

**ACHTUNG:** Diese Formulierung ergibt aktuell noch Basis=[s_1, s_2] statt [x_1, x_2].
Für Gomory-Schnitte ist Option 1 (manuelles Tableau) besser!

---

## Gomory-Schnitt berechnen

Optimale Lösung: x_1 = 4/3 = 1.333... (nicht ganzzahlig!)

**Fraktionaler Anteil:** 1/3 = 0.333...

**Gomory-Schnitt aus x_1-Zeile:**

Zeile: x_1 = 4/3 - 2/3·s_1 + 1/3·s_2

Gomory-Schnitt:
```
1/3 - 2/3·s_1 + 1/3·s_2 >= 0
```

Oder mit neuer Schlupfvariable s_3:
```
2/3·s_1 - 1/3·s_2 + s_3 = 1/3
```

Als Dezimalzahlen:
```
0.666667*s_1 - 0.333333*s_2 + s_3 = 0.333333
```

Dieses Constraint kann dann als neue Zeile ins Tableau eingefügt werden!

---

## Workflow in der App

1. **Anfangstableau lösen:**
   - Input: `x_1 + x_2` mit constraints `2*x_1 + x_2 <= 4, x_1 + 2*x_2 <= 4`
   - Click "🚀 Solve Automatically"
   - Ergebnis: x_1=1.333, x_2=1.333, Z=2.667

2. **Gomory-Schnitt berechnen:**
   - Fraktionaler Anteil von x_1: 0.333
   - Schnitt: 0.667*s_1 - 0.333*s_2 + s_3 = 0.333

3. **Neues Tableau mit Schnitt:**
   - Manuell neues Tableau erstellen (Option 1)
   - Oder: Create New Tableau mit 5 Variablen (x_1, x_2, s_1, s_2, s_3) und 3 Constraints
   - Neue Zeile für Gomory-Schnitt hinzufügen

4. **Weiter pivotieren:**
   - Dual-Simplex oder normale Simplex-Schritte
   - Bis ganzzahlige Lösung gefunden

---

## Wichtig für GLP (Ganzzahlige Lineare Programmierung)

- **Endtableau:** Decision variables (x_1, x_2, ...) in der Basis
- **Gomory-Schnitt:** Berechnet aus fraktionaler Zeile
- **Neue Restriktion:** Als Zeile ins Tableau einfügen
- **Basis:** Neue Schlupfvariable (s_3) kommt in Basis für neue Zeile

Die App unterstützt jetzt:
✅ Konstanten in Constraints (1.333 - 0.667*s_1 + ...)
✅ Manuelles Tableau mit beliebiger Basis
✅ Manipulation von Schlupfvariablen auch wenn decision variables in Basis

