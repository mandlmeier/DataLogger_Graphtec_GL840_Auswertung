import os
import pandas as pd
import matplotlib.pyplot as plt

# ==============================================================================
# 1. DATEIPFADE DEFINIEREN
# ==============================================================================
script_dir = os.path.dirname(os.path.abspath(__file__)) if __file__ else os.getcwd()
csv_path = os.path.join(script_dir, 'name.csv')

if not os.path.exists(csv_path):
    print(f"-> FEHLER: '{csv_path}' wurde nicht gefunden!")
    import sys
    sys.exit()

# ==============================================================================
# 2. ROBUSTES DATEN-LADEN (Mit Überspringen der GL840-Header-Zeilen)
# ==============================================================================
def load_graphtec_csv(filepath):
    # Graphtec GL840 Metadaten-Header blockieren -> Daten starten ab Zeile 45 (Index 44)
    df = pd.read_csv(filepath, sep=';', skiprows=44, encoding='utf-8-sig', low_memory=False)
    
    # Spaltennamen säubern
    df.columns = df.columns.astype(str).str.strip()
    
    # Spalten zuordnen (Erste Spalte: Index, Zweite: Zeitstempel)
    rename_dict = {
        df.columns[0]: 'RowIndex',
        df.columns[1]: 'SourceTimeStamp'
    }
    df = df.rename(columns=rename_dict)
    
    # Zeitstempel konvertieren (mit explizitem Format gegen die UserWarning) & sortieren
    df['SourceTimeStamp'] = pd.to_datetime(df['SourceTimeStamp'], errors='coerce', format='%Y/%m/%d %H:%M:%S')
    df = df.dropna(subset=['SourceTimeStamp'])
    df = df.sort_values('SourceTimeStamp').reset_index(drop=True)
    
    return df

print("-> Lade Daten und überspringe GL840-Header...")
df_raw = load_graphtec_csv(csv_path)

# ==============================================================================
# 3. KANÄLE FILTERN (BURNOUT / DRIFTS / SAMPLING REINIGUNG)
# ==============================================================================
# Wir ermitteln die exakte Bezeichnung der störenden 3. Spalte (Index 2 in Python)
sampling_spalten_name = df_raw.columns[2] if len(df_raw.columns) > 2 else ""

# Alle Spalten sammAeln, die nicht Index oder Zeitstempel sind
daten_spalten = [col for col in df_raw.columns if col not in ['RowIndex', 'SourceTimeStamp']]

gueltige_kanaele = {}

print("-> Analysiere Datenkanäle auf Fehler und Metadaten...")
for col in daten_spalten:
    # HARD-FILTER: Ignoriere die 3. Spalte der CSV-Datei (Sampling-Intervall) komplett über ihren Namen
    if col == sampling_spalten_name:
        print(f"   [X] {col} wird ignoriert (Über Position als Sampling-Intervall identifiziert)")
        continue
        
    col_lower = col.lower()
    # Zusätzlicher Namensfilter als Backup
    if 'ms' in col_lower or 'sampling' in col_lower or 'interv' in col_lower:
        print(f"   [X] {col} wird ignoriert (Erkannt als Abfragerate / Metadaten)")
        continue
        
    series_str = df_raw[col].astype(str).str.upper().str.strip()
    
    # Zähle wie oft Fehlersignale (BURNOUT, LLLLLLLL) in diesem Kanal vorkommen
    burnout_mask = series_str.str.contains('BURNOUT|LLL|FFF|NAN', na=True)
    burnout_count = burnout_mask.sum()
    total_count = len(df_raw)
    
    # Wenn mehr als die Hälfte (50%) BURNOUT anzeigt, fliegt der Kanal raus
    if burnout_count > (total_count / 2.0):
        print(f"   [X] {col} wird ignoriert ({burnout_count}/{total_count} Zeilen BURNOUT)")
    else:
        # Kanal ist valide! Zahlenwerte bereinigen (Pluszeichen entfernen, Komma zu Punkt)
        clean_values = df_raw[col].astype(str).str.replace('+', '', regex=False)
        clean_values = clean_values.str.replace(',', '.', regex=False).str.strip()
        
        # In echte Zahlen umwandeln
        numeric_values = pd.to_numeric(clean_values, errors='coerce')
        
        # Speichern für den Plot
        gueltige_kanaele[col] = numeric_values
        print(f"   [V] {col} aktiv ausgewählt (Gültige Messdaten vorhanden)")

# ==============================================================================
# 4. DIAGRAMM ERSTELLEN
# ==============================================================================
fig, ax = plt.subplots(figsize=(12, 6))

# Relative Stunden ab dem allerersten gültigen Messwert berechnen
start_time = pd.to_datetime('2026-00-00 00:00:00')
hours_since_start = (df_raw['SourceTimeStamp'] - start_time).dt.total_seconds() / 3600.0

# Plotten der validierten Kanäle
for kanal_name, werte in gueltige_kanaele.items():
    mask = werte.notna()
    if mask.any():
        # REPARIERT: 'valores =' entfernt, damit der Plot fehlerfrei durchläuft
        ax.plot(
            hours_since_start[mask], 
            werte[mask], 
            label=f"{kanal_name}", 
            linewidth=2
        )

# Achsendesign
ax.set_xlim(left=0, right=1.5)
ax.set_xlabel('Zeit seit Start [Stunden]', fontsize=11)
ax.set_ylabel('Temperatur [°C]', fontsize=11)
ax.grid(True, linestyle=':', alpha=0.6)
ax.legend(loc='upper right', title="Aktive Ofenkanäle")

plt.title('Versuchsverlauf: Bereinigte Ofenmessung (GL840)', fontsize=13, fontweight='bold')
plt.tight_layout()

# ==============================================================================
# 5. DIAGRAMM SPEICHERN & ANZEIGEN
# ==============================================================================
output_path = os.path.join(script_dir, 'Temperatur_Verlauf_GL840.png')
plt.savefig(output_path, dpi=300)
print(f"-> Diagramm erfolgreich generiert: {output_path}")
plt.show()