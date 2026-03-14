# 🎓 Interaktiver Simplex-Tableau-Rechner

> **Entwickelt für das Studienmodul Operations Research**
> Von der linearen Programmierung (LP) zur ganzzahligen linearen Programmierung (ILP/GLP) mit Gomory-Schnitten

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://simplex-gomory.streamlit.app/)

---

## 📚 Motivation & Hintergrund

Dieses Tool entstand im Rahmen des Studienmoduls **Operations Research** und adressiert ein zentrales Problem:

### Das Problem
**Ganzzahlige Lineare Programmierung (GLP/ILP)** ist in der Praxis allgegenwärtig:
- Produktionsplanung (man kann keine halben Maschinen produzieren)
- Transportoptimierung (Anzahl LKWs muss ganzzahlig sein)
- Personaleinsatzplanung (keine halben Mitarbeiter)

### Der Lösungsweg
1. **LP-Problem lösen** mit dem Simplex-Algorithmus → optimale Lösung (oft nicht ganzzahlig)
2. **Gomory-Schnitte hinzufügen** → neue Nebenbedingungen, die fraktionale Lösungen ausschließen
3. **Weiter pivotieren** im Endtableau → ganzzahlige optimale Lösung

### Die Herausforderung
Bestehende Tools erlauben keine **manuelle Manipulation des Endtableaus** – genau das, was für Gomory-Schnitte benötigt wird! Man braucht:
- Zugriff auf das Endtableau mit **decision variables in der Basis**
- Möglichkeit, **Schlupfvariablen zu optimieren** (nicht nur decision variables)
- **Neue Zeilen hinzufügen** (Gomory-Schnitte)
- **Schritt-für-Schritt Nachvollziehbarkeit** für das Verständnis

**→ Dieses Tool schließt diese Lücke!**

---

## ✨ Features

### 🎯 Kernfunktionalität
- **Flexible Expression-Eingabe**: `3*x_1 + 4*x_2`, `2*x_1 + 3*x_2 <= 18`
- **Automatische Lösung**: Ein Klick zum optimalen Tableau
- **Manuelle Pivot-Operationen**: Vollständige Kontrolle über jeden Schritt
- **Endtableau-Modus**: Für Gomory-Schnitte (ohne artificial variables)
- **History-Navigation**: Alle Zwischenschritte durchgehen

### 🌐 Benutzerfreundlichkeit
- **Zweisprachig**: 🇩🇪 Deutsch / 🇬🇧 English
- **Schöne LaTeX-Darstellung**: Gleichungssysteme mit ≥ / ≤ Symbolen
- **Interaktive Tableaus**: Farbcodierte Pivot-Elemente
- **Minimum-Ratio-Test**: Automatische Berechnung mit Tabelle
- **Complete Solution Vector**: Alle Variablen (basic & non-basic)

### 🔧 Erweiterte Funktionen
- **Big-M Methode**: Automatisch für ≥ und = Constraints
- **Konstanten in Ausdrücken**: `2.667 - 0.333*s_1 + 1.5`
- **Beliebige Basis**: Decision variables oder Slack variables
- **Degeneracy Detection**: Warnung bei entarteten Lösungen
- **Unbounded Detection**: Erkennung unbeschränkter Probleme

---

## 🚀 Schnellstart

### Online (empfohlen)
Einfach öffnen: **[simplex-gomory.streamlit.app](https://simplex-gomory.streamlit.app/)**

### Lokal installieren
```bash
# Repository klonen
git clone https://github.com/Max-imalgutaussehend/complex_simplex_calculator.git
cd complex_simplex_calculator

# Dependencies installieren
pip install -r requirements.txt

# App starten
streamlit run app.py
```

Öffne Browser: `http://localhost:8501`

---

## 📖 Anwendungsbeispiele

### Beispiel 1: Standard-LP lösen

**Problem:**
```
Maximiere: x₁ + x₂
Nebenbedingungen:
  2x₁ + x₂ ≤ 4
  x₁ + 2x₂ ≤ 4
  x₁, x₂ ≥ 0
```

**In der App:**
1. **Objective**: `x_1 + x_2`
2. **Constraints**: `2*x_1 + x_2 <= 4, x_1 + 2*x_2 <= 4`
3. **Klick**: "🚀 Automatisch lösen"

**Ergebnis:**
- Z = 2.667
- x₁ = 1.333, x₂ = 1.333 ⚠️ (nicht ganzzahlig!)

---

### Beispiel 2: Gomory-Schnitte für ILP

**Situation nach LP-Lösung:**
- Optimale Lösung: x₁ = 4/3, x₂ = 4/3
- Problem: Nicht ganzzahlig!

**Schritt 1: Endtableau aufrufen**

✅ **Endtableau-Modus** aktivieren (Checkbox in Sidebar)

**Input:**
```
Objective: 2.666667 - 0.333333*s_1 - 0.333333*s_2
Constraints:
  x_1 - 0.666667*s_1 + 0.333333*s_2 = 1.333333,
  x_2 + 0.333333*s_1 - 0.666667*s_2 = 1.333333
```

**Ergebnis:**
```
x₁ = 4/3 - 2/3·s₁ + 1/3·s₂ ≥ 0
x₂ = 4/3 + 1/3·s₁ - 2/3·s₂ ≥ 0
s₁ ≥ 0
s₂ ≥ 0
Z = 8/3 - 1/3·s₁ - 1/3·s₂
```

**Schritt 2: Gomory-Schnitt berechnen**

Aus der Zeile `x₁ = 4/3 - 2/3·s₁ + 1/3·s₂`:
- Fraktionaler Anteil von 4/3 = 1/3
- Gomory-Schnitt: `s₃ = 1/3 - 2/3·s₁ + 1/3·s₂`

**Schritt 3: Neues Tableau mit Schnitt**

Verwende "Create New Tableau" Modus:
- 5 Variablen (x₁, x₂, s₁, s₂, s₃)
- 3 Constraints (2 original + 1 Gomory)
- Weiter pivotieren bis ganzzahlige Lösung

---

### Beispiel 3: Großes Problem (14 Variablen)

**Real-world Produktionsplanung:**

```
Objective: 50*x_1+100*x_2+100*x_3+...+100*x_14

Constraints:
-50*x_1-100*x_2-100*x_4+50*x_8+100*x_10>=-30,
-50*x_1-100*x_3-100*x_5+50*x_9+100*x_11>=-30,
-50*x_2-100*x_6+50*x_10+100*x_12>=-20,
-50*x_3-100*x_7+50*x_11+100*x_13>=-20,
50*x_4+100*x_6+50*x_12-100*x_14>=-20,
50*x_5+100*x_7+50*x_13-100*x_14>=-20,
x_1+x_2+x_3<=1,
x_4+x_5<=1,
x_6+x_7<=1,
x_8+x_9<=1,
x_10+x_11<=1,
x_12+x_13<=1
```

**Ergebnis nach Auto-Solve:**
- Z = 42.72
- Optimale Werte für alle 14 Variablen
- Gelöst in wenigen Sekunden

---

## 🎨 Features im Detail

### 📐 Schöne Tableau-Darstellung

Jedes Tableau wird angezeigt als:

**1. LaTeX-Gleichungssystem** (expandable)
```
s₁ = 4 - 2·x₁ - 1·x₂ ≥ 0
s₂ = 4 - 1·x₁ - 2·x₂ ≥ 0
x₁ ≥ 0
x₂ ≥ 0
Z = 0 + 1·x₁ + 1·x₂
```

**2. Traditionelle Matrix**
```
     x₁   x₂   s₁   s₂  RHS
s₁   2.0  1.0  1.0  0.0  4.0
s₂   1.0  2.0  0.0  1.0  4.0
z   -1.0 -1.0  0.0  0.0  0.0
```

**3. Aktuelle Lösung**
- Basisvariablen mit Werten
- Nichtbasisvariablen = 0
- Z-Wert prominent

### 🔄 Workflow-Features

**Nach Auto-Solve:**
- ✅ Status: OPTIMAL
- 📊 Vollständiger Lösungsvektor
- 📈 Anzahl Iterationen
- 🔄 "Neues Problem" Button → Reset für nächstes Problem

**Während manueller Pivots:**
- Eingangsvariable wählen (mit Hints: "Improving: x₁, x₂")
- Ausgangsvariable wählen (mit Ratios: "s₁ (ratio: 6.0)")
- Pivot-Details expandable (Minimum-Ratio-Test)
- History-Navigation (Vorheriger/Nächster Schritt)

---

## 🏗️ Architektur

### Dateistruktur
```
complex_simplex_calculator/
├── app.py                  # Streamlit UI (Hauptanwendung)
├── simplex.py             # Simplex-Algorithmus Logik
├── parser.py              # Expression Parser (Big-M Methode)
├── translations.py        # Deutsch/English Übersetzungen
├── tableau_renderer.py    # LaTeX-Rendering für Tableaus
├── requirements.txt       # Python Dependencies
└── README.md             # Diese Datei
```

### Technologie-Stack
- **Framework**: Streamlit (Python)
- **Numerik**: NumPy, Pandas
- **Visualisierung**: LaTeX (via st.latex), Matplotlib
- **Deployment**: Streamlit Cloud

---

## 🎓 Akademischer Nutzen

### Für Studierende
- ✅ **Verstehen** des Simplex-Algorithmus durch Visualisierung
- ✅ **Üben** von Pivot-Operationen Schritt für Schritt
- ✅ **Lernen** der Gomory-Schnitt-Methode praktisch
- ✅ **Verifizieren** von Hausaufgaben/Klausuraufgaben
- ✅ **Experimentieren** mit verschiedenen LP-Formulierungen

### Für Dozenten
- ✅ **Demonstrieren** der Algorithmen live in Vorlesungen
- ✅ **Erstellen** von interaktiven Übungsaufgaben
- ✅ **Zeigen** der Verbindung LP → ILP
- ✅ **Erklären** von Degeneracy, Unboundedness, etc.

---

## 🤝 Beitragen

Contributions sind willkommen! Besonders:
- Neue Beispiele für Gomory-Schnitte
- Übersetzungen in weitere Sprachen
- UI/UX Verbesserungen
- Zusätzliche OR-Algorithmen (Dualer Simplex, etc.)

**Issues & Pull Requests**: [GitHub Repository](https://github.com/Max-imalgutaussehend/complex_simplex_calculator)

---

## 📝 Lizenz

MIT License - Frei verwendbar für akademische und kommerzielle Zwecke.

---

## 🙏 Danksagung

Entwickelt im Rahmen des Studienmoduls **Operations Research** zur Unterstützung des Lernens von LP- und ILP-Optimierung.

**Besonderer Dank an:**
- Die Streamlit-Community für das großartige Framework
- Dozenten und Kommilitonen für Feedback und Testcases

---

## 📧 Kontakt

Bei Fragen, Bugs oder Feature-Requests:
- **GitHub Issues**: [Issues erstellen](https://github.com/Max-imalgutaussehend/complex_simplex_calculator/issues)
- **GitHub**: [@Max-imalgutaussehend](https://github.com/Max-imalgutaussehend)

---

**⭐ Wenn dir das Tool hilft, gib dem Repo einen Star auf GitHub!**

*Entwickelt mit ❤️ für Operations Research*
