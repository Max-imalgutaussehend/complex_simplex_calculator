# Automatischer Simplex-Rechner - Anleitung

## Neue Features

### 🚀 Auto-Solve Button

Klicke auf **"Solve Automatically"** um das Problem in einem Schritt zu lösen!

Der Rechner:
- ✅ Führt alle Pivot-Operationen automatisch durch
- ✅ Zeigt alle Zwischen-Tableaus in der History
- ✅ Findet die optimale Lösung
- ✅ Zeigt den kompletten Lösungsvektor

---

## Verwendung

### 1. Problem eingeben

**Expression Input Mode:**
```
Objective: 3*x_1 + 4*x_2
Constraints: 2*x_1 + 3*x_2 <= 18, 2*x_1 + x_2 <= 12
```

Klicke: **"Create Tableau from Expressions"**

### 2. Automatisch lösen

Klicke: **"🚀 Solve Automatically"**

Der Rechner führt alle Iterationen durch!

### 3. Ergebnis ansehen

#### Direktanzeige:
- **Z = 25.5000** (Optimal!)
- **Status: OPTIMAL** ✓
- **Pivot Steps: 2** (Anzahl Iterationen)

#### Current Solution:
**Basic Variables:**
- x_2 = 3.0000
- x_1 = 4.5000

**Non-basic Variables:**
- s_1 = 0.0000
- s_2 = 0.0000

#### Complete Solution Vector:
Klicke auf **"📊 Complete Solution Vector"** für Details:

| Variable | Value     | Basic |
|----------|-----------|-------|
| x_1      | 4.500000  | ✓     |
| x_2      | 3.000000  | ✓     |
| s_1      | 0.000000  |       |
| s_2      | 0.000000  |       |

**Summary:**
- Decision variables: 2
- Slack variables: 2
- Basic variables: 2
- Non-basic (zero): 2

---

## Zwischen-Tableaus ansehen

Nach Auto-Solve kannst du die History-Navigation verwenden:

- **First Step** → Initiales Tableau
- **Previous Step** → Vorherige Iteration
- **Next Step** → Nächste Iteration

So siehst du jeden Pivot-Schritt!

---

## Beispiel: Großes Problem

```
Objective: x_1 + x_2 + x_3 + x_4 + x_5 + x_6 + x_7 + x_8 + x_9 + x_10

Constraints:
3*x_1 + x_2 + 2*x_3 + x_4 + x_5 + x_6 + x_7 + x_8 + x_9 + x_10 <= 30,
x_1 <= 1,
x_2 <= 1,
x_3 <= 1,
x_4 <= 1,
x_5 <= 1,
x_6 <= 1,
x_7 <= 1,
x_8 <= 1,
x_9 <= 1,
x_10 <= 1
```

**Ergebnis nach Auto-Solve:**
- Z = optimal value
- Alle x_i Werte
- Alle s_i Werte
- Anzahl Iterationen

---

## Was wird berechnet?

### Z-Wert (Zielfunktion)
```
Z = c₁·x₁ + c₂·x₂ + ... + cₙ·xₙ
```

Für Basic Variables: Z = Summe der (Koeffizient × Wert)

**Beispiel:**
- Objective: 3*x_1 + 4*x_2
- Solution: x_1=4.5, x_2=3.0
- Z = 3×4.5 + 4×3.0 = 13.5 + 12.0 = **25.5** ✓

### Lösungsvektor
```
x = [x_1, x_2, ..., xₙ, s_1, s_2, ..., sₘ]ᵀ
```

**Basic Variables:** Werte aus RHS-Spalte
**Non-basic Variables:** = 0

---

## Initiales vs Optimales Tableau

### Initiales Tableau
- **Basis:** Schlupfvariablen (s_1, s_2, ...)
- **Z = 0** (weil alle x_i = 0)
- **Status:** Not optimal

### Nach 1. Iteration
- **Basis:** Gemischt (z.B. x_2, s_2)
- **Z > 0** (Verbesserung!)
- **Status:** Not optimal

### Optimales Tableau
- **Basis:** Optimal gewählte Variablen
- **Z = Maximum** (bei Maximierung)
- **Status:** OPTIMAL ✓
- **Alle reduced costs ≥ 0**

---

## Degeneracy (Entartung)

Wenn du siehst: **"Degenerate solution"**

Das bedeutet: Eine oder mehrere Basisvariablen = 0

**Ist das ein Problem?**
- Nein! Der Algorithmus funktioniert trotzdem
- Kann aber zu mehr Iterationen führen
- Lösung ist trotzdem korrekt

---

## Tipps

### Schnelle Lösung
1. Problem eingeben
2. "Solve Automatically" klicken
3. Fertig!

### Lernmodus
1. Problem eingeben
2. Manuell pivotieren (Schritt für Schritt)
3. Jeden Schritt verstehen
4. Oder: Auto-Solve + History durchgehen

### Fehlersuche
Wenn Z falsch erscheint:
- Initial: Z = 0 ist korrekt (alle x_i = 0)
- Nach Pivots: Z sollte steigen (bei max)
- Optimal: Z = Maximum

---

## Technische Details

### Auto-Solve Algorithmus
1. Wähle Variable mit negativstem reduced cost (steepest descent)
2. Führe Minimum Ratio Test durch
3. Pivot ausführen
4. Wiederholen bis optimal
5. Maximum 100 Iterationen (Schutz vor Cycling)

### Komplexität
- Worst-case: Exponentiell (selten)
- Typical: Polynomial
- Für dein Problem: Wenige Iterationen

---

## Vergleich: Manuell vs Automatisch

| Feature | Manuell | Automatisch |
|---------|---------|-------------|
| Kontrolle | Vollständig | Keine |
| Geschwindigkeit | Langsam | Sofort |
| Lernen | Optimal | Gut (History) |
| Fehleranfällig | Ja | Nein |
| Große Probleme | Mühsam | Einfach |

**Empfehlung:**
- Kleine Probleme (≤ 3 Variablen): Manuell
- Große Probleme (> 3 Variablen): Automatisch
- Lernen: Beides kombinieren!

---

## Häufige Fragen

### F: Warum zeigt Initial-Tableau Z = 0?
**A:** Korrekt! Alle x_i = 0 am Start (Basis = Schlupfvariablen)

### F: Wie bekomme ich Z = 42?
**A:** Nach Auto-Solve, wenn optimale Lösung Z = 42 ergibt

### F: Was ist der Lösungsvektor?
**A:** Alle Variablenwerte: x₁, ..., xₙ, s₁, ..., sₘ

### F: Muss ich alle Iterationen sehen?
**A:** Nein! Auto-Solve springt direkt zur Lösung. History ist optional.

### F: Kann ich Zwischenschritte ansehen?
**A:** Ja! Mit History-Navigation nach Auto-Solve

---

## Beispiel-Ablauf

```
1. Eingabe:
   Objective: 3*x_1 + 4*x_2
   Constraints: 2*x_1 + 3*x_2 <= 18, 2*x_1 + x_2 <= 12

2. Initial:
   Z = 0.0000
   Basis: [s_1, s_2]
   Status: Not optimal

3. Klick "Solve Automatically"

4. Optimal:
   Z = 25.5000 ✓
   Basis: [x_2, x_1]
   Status: OPTIMAL
   Iterations: 2

5. Solution:
   x_1 = 4.5000
   x_2 = 3.0000
   s_1 = 0.0000
   s_2 = 0.0000
```

---

**Viel Erfolg mit dem automatischen Simplex-Rechner!** 🚀
