# SkyShield-ATC v3.0

### Cybersecurity Defense and Intrusion Detection Simulation for Air Traffic Control Networks

**Author:** Amir Hossein Rashidi
**Affiliation:** Islamic Azad University, Tehran Central Branch
**Research Area:** Air Traffic Control (ATC) Cybersecurity

---

## Overview

**SkyShield-ATC** is an interactive Python-based simulation environment developed to demonstrate cybersecurity threats and defensive mechanisms in modern **Air Traffic Control (ATC)** communication networks.

The project is based on the research paper:

> **"Analysis of Vulnerabilities and Provision of Advanced Security Solutions for Communication Protocols in Air Traffic Control Networks"**

The paper analyzes the security weaknesses of major aviation communication and surveillance protocols, including:

* ADS-B
* TCAS
* CPDLC
* LDACS

and investigates several practical attack scenarios, including:

* Ghost Aircraft Injection
* TCAS Distance Spoofing
* Replay Attacks
* GPS Spoofing combined with ADS-B Injection
* Denial-of-Service (DoS) / Frequency Flooding

The proposed security architecture combines real-time anomaly detection, physical/timing-based validation, post-quantum authentication, and blockchain-based secondary verification.

---

# Project Purpose

The primary objective of this project is to provide a visual and interactive demonstration of how cyberattacks against ATC surveillance systems can be simulated and how different detection and protection layers can respond to those threats.

The application provides a radar-style interface where aircraft are continuously simulated and security events can be injected dynamically.

The implementation is intended primarily for:

* Academic demonstrations
* ATC cybersecurity research
* Intrusion Detection System (IDS) concepts
* Aviation cybersecurity education
* Security architecture visualization
* Demonstration of ADS-B-related attack scenarios

---

# Research Background

Modern ATC systems increasingly rely on digital communication and surveillance protocols. The research paper identifies fundamental security limitations in several aviation protocols, particularly the lack of strong authentication, encryption limitations, and the broadcast nature of ADS-B communications.

ADS-B is particularly important because aircraft broadcast information such as:

* Aircraft identification
* Position
* Altitude
* Velocity
* Surveillance information

without providing strong native message authentication or end-to-end encryption.

These characteristics create opportunities for attackers to inject, replay, manipulate, or flood aviation surveillance traffic.

---

# Supported Attack Scenarios

SkyShield-ATC provides interactive simulation of five major attack categories described in the research.

## 1. Ghost Aircraft Injection

The simulator can introduce artificial aircraft into the surveillance environment.

The generated ghost aircraft are configured with abnormal characteristics such as unusually high speeds and inconsistent surveillance information.

The implementation creates ghost aircraft with speeds between approximately **1250–1450 km/h**, together with TDoA and PSR-related inconsistencies.

This scenario represents the Ghost Aircraft Injection attack discussed in Section 3.1 of the paper.

The paper describes this attack as the injection of fabricated ADS-B messages containing attacker-controlled aircraft information.

---

## 2. TCAS Distance Spoofing

The simulator supports a TCAS spoofing scenario in which the perceived distance associated with a target is manipulated.

The implementation uses a spoofed distance greater than **3.5 km** and marks the simulated aircraft as a TCAS-related threat.

The threshold is based on the attack scenario discussed in the research paper, where manipulation of perceived target distance can potentially trigger inappropriate Resolution Advisories.

---

## 3. Replay Attack

The simulator can create a duplicate aircraft by selecting an existing legitimate aircraft and generating a delayed/replayed representation.

The implementation models:

* Duplicate targets
* Modified position
* Slightly modified velocity
* Timestamp inconsistency
* Approximate replay delay

The attack is associated with the paper's Section 3.2 Replay Attack scenario.

The paper describes replay attacks as the retransmission of previously captured legitimate ADS-B messages at a different time or location.

---

## 4. GPS Spoofing + ADS-B Injection

The simulator provides a combined GPS spoofing and ADS-B injection scenario.

A GPS offset is assigned to a selected legitimate aircraft while a separate malicious aircraft can simultaneously be injected into the simulated surveillance environment.

The implementation therefore demonstrates the relationship between:

```text
GPS Spoofing
      +
ADS-B Injection
      ↓
Manipulated Aircraft Position
      ↓
Inconsistent Surveillance Information
```

This corresponds to the combined attack scenario discussed in Section 3.3 of the research.

---

## 5. DoS / Frequency Flooding

The simulator also provides a flooding scenario targeting the **1090 MHz Mode-S channel**.

When the attack is activated, multiple phantom signals are introduced into the simulated environment.

The implementation generates **16 phantom aircraft/signals** for the visual simulation.

The research paper identifies 1090 MHz as a shared channel and discusses the possibility of channel saturation through large numbers of fabricated messages.

> **Important:** The implementation is a simulation of the attack concept. It does not transmit actual RF signals or perform real-world 1090 MHz interference.

---

# Intrusion Detection

The application provides multiple IDS modes:

| Detection Method    | Reported Accuracy | Reported FPR | Reported Latency |
| ------------------- | ----------------: | -----------: | ---------------: |
| LSTM                |             98.7% |         1.2% |            15 ms |
| Random Forest       |             93.4% |         3.8% |             8 ms |
| SVM                 |             89.2% |         6.1% |             5 ms |
| Multi-Sensor Fusion |             99.1% |         0.7% |            25 ms |

These values correspond to the comparative results presented in the paper and are also exposed through the application's monitoring interface.

The paper reports the same comparison in its machine-learning-based intrusion detection discussion.

---

# Important Implementation Note

Although the user interface labels one detection mode as **LSTM**, the current Python implementation does **not** contain an actual recurrent LSTM network.

Instead, the implementation creates:

```python
MLPClassifier(
    hidden_layer_sizes=(128, 128, 128),
    max_iter=1000,
    random_state=42,
    learning_rate_init=0.001
)
```

and assigns it to the variable:

```python
clf_lstm
```

The other implemented classifiers are:

```python
RandomForestClassifier(
    n_estimators=100,
    random_state=42
)
```

and:

```python
SVC(
    kernel='rbf',
    probability=True,
    random_state=42
)
```

These models are trained using a small built-in demonstration dataset.

Therefore, this repository should be considered a **research prototype and interactive simulation**, rather than a production-grade LSTM-based ATC IDS.

---

# Detection Features

The detection process uses five input features:

```text
1. Aircraft speed
2. TDoA
3. PSR consistency
4. TCAS indicator
5. GPS attack indicator
```

The implementation constructs the feature vector as:

```text
[speed, TDoA, PSR, TCAS, GPS]
```

and passes it to the selected classifier.

For the multi-sensor mode, PSR/ADS-B mismatch can additionally influence the detection decision.

This reflects the research paper's proposal to combine ADS-B information with Primary Surveillance Radar (PSR) data for cross-validation.

---

# TDoA-Based Validation

The research framework proposes timing-based detection using:

* ToA — Time of Arrival
* TDoA — Time Difference of Arrival

The goal is to determine whether the physical origin of a transmission is consistent with the reported aircraft location.

The paper describes the use of multiple receivers to estimate the transmitter position and discusses meter-level localization accuracy in experimental scenarios.

SkyShield-ATC incorporates TDoA-related information into its simulated aircraft state and displays TDoA-related telemetry in the interface.

---

# Proposed Three-Layer Security Architecture

The research paper proposes a three-layer security architecture.

```text
┌──────────────────────────────────────────────┐
│       Layer 3 — Blockchain Verification      │
│       Flight-path secondary verification     │
├──────────────────────────────────────────────┤
│       Layer 2 — Authentication & Crypto      │
│       ML-DSA / PQC / PUF                     │
├──────────────────────────────────────────────┤
│       Layer 1 — Real-Time Detection          │
│       ML + TDoA + Multi-Sensor Validation    │
└──────────────────────────────────────────────┘
```

The three layers proposed by the paper are:

### Layer 1 — Real-Time Anomaly Detection

The research proposes:

* Bidirectional LSTM analysis
* Primary radar cross-validation
* ToA/TDoA-based transmitter localization

### Layer 2 — Authentication and Cryptography

The paper proposes:

* ML-DSA digital signatures
* Modeling-resistant PUF authentication
* Gradual migration toward post-quantum cryptography

### Layer 3 — Blockchain-Based Secondary Verification

The proposed architecture uses blockchain to maintain an additional record of aircraft flight paths and provide secondary verification for suspicious situations.

The paper proposes periodic flight-path registration and a lightweight consensus mechanism.

---

# Implementation of the Three Layers

The GUI exposes the three layers as independent switches:

```text
L1 — LSTM + TDoA
L2 — ML-DSA
L3 — Blockchain
```

The corresponding implementation variables are:

```python
self.ids_var
self.pqc_var
self.bc_var
```

with the default configuration enabling IDS while disabling the PQC and blockchain layers.

---

# Security Framework Performance

The application also provides a simulated representation of the complete three-layer framework.

When all three layers are enabled, the interface displays:

```text
Accuracy : 99.4%
FPR      : 0.2%
Latency  : 68 ms
```

These values are represented directly in the application's telemetry logic.

The values should be interpreted as **reported/proposed framework performance from the research model**, not as independently reproduced experimental measurements generated by this Python script.

---

# Post-Quantum Cryptography

The research paper proposes **ML-DSA** as a post-quantum digital-signature mechanism for critical ATC messages.

The paper discusses the size and latency considerations associated with post-quantum signatures and notes that directly adding a large digital signature to a short ADS-B message is impractical.

The application therefore represents ML-DSA as a configurable security layer:

```text
L2 — ML-DSA
```

and displays the key/signature sizes used by the proposed framework:

```text
Key:       2880 bytes
Signature: 2420 bytes
```

> **Implementation limitation:** The current script does not implement an actual ML-DSA cryptographic operation. The ML-DSA component is represented as a configurable architectural/simulation layer.

---

# Blockchain Layer

The paper proposes blockchain as a secondary verification mechanism for suspicious aircraft trajectories.

The current application maintains a blockchain-related ledger state and exposes the blockchain layer through the GUI. However, this implementation should be understood as a **simulation/prototype representation** rather than a complete production blockchain network.

The architecture itself follows the paper's proposal of using blockchain as a secondary verification layer rather than relying on it for latency-critical functions such as TCAS.

---

# User Interface

SkyShield-ATC provides a radar-style graphical interface implemented with **Tkinter**.

The interface contains:

* Real-time radar visualization
* Aircraft tracking
* Attack injection controls
* IDS selection
* Security-layer controls
* Threat counter
* TDoA telemetry
* Security logs
* Performance indicators
* PQC status
* Blockchain status

The application uses a continuously animated canvas and updates the visualization approximately every 40 ms.

---

# Architecture

The high-level implementation can be represented as:

```text
                     SkyShield-ATC
                           │
             ┌─────────────┴─────────────┐
             │                           │
        Traffic Model              Attack Engine
             │                           │
             │              ┌────────────┼────────────┐
             │              │            │            │
             │           Ghost         Replay       GPS
             │           TCAS          DoS           Spoof
             │
             ▼
       Feature Extraction
             │
             ├── Speed
             ├── TDoA
             ├── PSR
             ├── TCAS
             └── GPS
             │
             ▼
       Intrusion Detection
             │
       ┌─────┼─────┐
       │     │     │
      MLP    RF    SVM
       │
       ▼
   Threat Decision
       │
       ├── TDoA / PSR validation
       ├── ML-DSA layer representation
       └── Blockchain layer representation
       │
       ▼
   Radar Visualization
       +
   Security Telemetry
       +
   Event Logging
```

---

# Technologies

The project is implemented in Python using:

* Python 3
* Tkinter
* NumPy
* scikit-learn
* Mathematical utilities
* Randomized simulation
* Real-time GUI animation

The source code imports `Tkinter`, `NumPy`, `MLPClassifier`, `RandomForestClassifier`, and `SVC`.

---

# Requirements

Install the required Python packages:

```bash
pip install numpy scikit-learn
```

Tkinter is normally included with standard Python installations on Windows.

On Debian/Ubuntu-based Linux systems, install it with:

```bash
sudo apt install python3-tk
```

---

# Installation

Clone the repository:

```bash
git clone https://github.com/<YOUR-USERNAME>/<YOUR-REPOSITORY>.git
cd <YOUR-REPOSITORY>
```

Install dependencies:

```bash
pip install numpy scikit-learn
```

Then run:

```bash
python "ATC System Amir Hossein Rashidi(3).py"
```

---

# Running the Application

After launching the program, the SkyShield-ATC interface opens in fullscreen mode.

The application initializes several simulated aircraft and starts the real-time radar animation automatically.

### Keyboard Controls

| Key   | Function         |
| ----- | ---------------- |
| `Esc` | Exit fullscreen  |
| `F11` | Enter fullscreen |

---

# Attack Simulation Controls

The left-side control panel provides buttons for:

```text
Ghost Aircraft Injection
TCAS Spoofing
Replay Attack
GPS Spoofing
DoS Flooding
Clear All Threats
```

These attack controls correspond directly to the attack categories analyzed in the paper.

---

# IDS Selection

The user can switch between the available detection modes:

```text
LSTM
Random Forest
SVM
Multi-Sensor
```

The GUI associates each mode with the corresponding reported performance values from the research comparison.

---

# Security Layer Controls

The application provides three configurable security layers:

```text
[✓] L1 — LSTM + TDoA
[ ] L2 — ML-DSA
[ ] L3 — Blockchain
```

Users can enable or disable these components and observe the corresponding telemetry changes.

---

# Example Workflow

A typical demonstration can be performed as follows:

### Step 1 — Start the simulator

```bash
python "ATC System Amir Hossein Rashidi(3).py"
```

### Step 2 — Observe normal traffic

The simulator initializes legitimate aircraft and displays them on the radar.

### Step 3 — Inject a Ghost Aircraft

Activate:

```text
Ghost Aircraft Injection
```

Observe:

* New aircraft target
* Abnormal speed
* TDoA inconsistency
* Threat indication
* Security log

### Step 4 — Test Replay Detection

Activate:

```text
Replay Attack
```

Observe the duplicated target and timestamp-related anomaly.

### Step 5 — Test GPS Spoofing

Activate:

```text
GPS Spoofing
```

Observe the manipulated aircraft position and simultaneous ADS-B injection.

### Step 6 — Test DoS Flooding

Activate:

```text
DoS Flooding
```

Observe the increased number of phantom targets.

### Step 7 — Enable Security Layers

Enable:

```text
L1 — IDS + TDoA
L2 — ML-DSA
L3 — Blockchain
```

The application then displays the complete simulated security framework.

---

# Research-to-Code Mapping

| Research Paper Component | Implementation                            |
| ------------------------ | ----------------------------------------- |
| ADS-B security analysis  | ADS-B surveillance simulation             |
| Ghost Aircraft Injection | `atk_ghost()`                             |
| TCAS Spoofing            | `atk_tcas()`                              |
| Replay Attack            | `atk_replay()`                            |
| GPS Spoofing             | `atk_gps()`                               |
| DoS/Flooding             | `atk_flood()`                             |
| Machine-learning IDS     | MLP / RF / SVM                            |
| TDoA analysis            | Aircraft TDoA state + telemetry           |
| PSR validation           | PSR feature and mismatch logic            |
| PQC / ML-DSA             | Configurable simulation layer             |
| Blockchain               | Configurable secondary-verification layer |
| Three-layer framework    | L1 + L2 + L3 GUI controls                 |
| Security telemetry       | Real-time GUI metrics                     |
| Attack logging           | Real-time event log                       |

The attack functions and corresponding paper section references are explicitly embedded in the source code.

---

# Project Structure

For the current single-file implementation:

```text
SkyShield-ATC/
│
├── ATC System Amir Hossein Rashidi(3).py
├── README.md
└── requirements.txt
```

A future modular version could be organized as:

```text
SkyShield-ATC/
│
├── src/
│   ├── main.py
│   ├── simulation/
│   │   ├── aircraft.py
│   │   └── traffic.py
│   │
│   ├── attacks/
│   │   ├── ghost.py
│   │   ├── tcas.py
│   │   ├── replay.py
│   │   ├── gps.py
│   │   └── dos.py
│   │
│   ├── detection/
│   │   ├── mlp.py
│   │   ├── random_forest.py
│   │   ├── svm.py
│   │   └── multisensor.py
│   │
│   ├── security/
│   │   ├── tdoa.py
│   │   ├── pqc.py
│   │   └── blockchain.py
│   │
│   └── gui/
│       └── dashboard.py
│
├── requirements.txt
├── README.md
└── LICENSE
```

---

# Current Prototype Limitations

This project should be considered a **research and educational prototype**.

Important limitations include:

1. The current implementation does not communicate with real ADS-B receivers.
2. It does not transmit or interfere with real 1090 MHz RF signals.
3. The displayed aircraft are simulated.
4. The ML training dataset embedded in the source code is very small.
5. The variable named `clf_lstm` is implemented using `MLPClassifier`, not an actual LSTM architecture.
6. ML-DSA is represented as a security layer but is not cryptographically executed.
7. The blockchain component represents the architectural concept rather than a complete distributed blockchain implementation.
8. The reported accuracy/FPR/latency values are primarily research-paper/reference values displayed by the simulation rather than results independently reproduced by this script.

These distinctions are important when using the project for academic or research purposes.

---

# Relation to the Research Paper

The research paper proposes a comprehensive security architecture consisting of real-time anomaly detection, authentication/cryptography, and blockchain-based secondary verification.

SkyShield-ATC translates these concepts into an interactive simulation environment.

The relationship can be summarized as:

```text
Research Paper
      │
      ├── ATC Protocol Vulnerabilities
      │
      ├── Attack Classification
      │
      ├── ML-Based Detection
      │
      ├── TDoA / Multi-Sensor Validation
      │
      ├── Post-Quantum Authentication
      │
      └── Blockchain Verification
               │
               ▼
        SkyShield-ATC
               │
               ├── Attack Simulation
               ├── IDS Demonstration
               ├── TDoA Visualization
               ├── PQC Layer Simulation
               ├── Blockchain Layer Simulation
               └── Real-Time Security Dashboard
```

---

# Future Development

The project can be extended toward a more realistic experimental platform by implementing:

* Real ADS-B/Mode-S data ingestion
* Public ADS-B datasets
* Real LSTM/BiLSTM models
* Larger and balanced training datasets
* Feature normalization and preprocessing
* Model evaluation using Accuracy, Precision, Recall, F1, ROC-AUC
* Real TDoA multilateration
* PSR/ADS-B sensor fusion
* Actual ML-DSA cryptographic operations
* Real PUF-based authentication experiments
* Permissioned blockchain implementation
* Adversarial machine-learning evaluation
* SDR-based laboratory experiments
* Network packet capture and replay analysis
* Dockerized deployment
* REST/API integration
* SOC/SIEM integration

These directions are consistent with the research paper's proposed adaptive IDS, post-quantum authentication, PUF-based authentication, and blockchain-based secondary verification architecture.

---

# Academic Context

This project is an implementation-oriented companion to the research work:

**Analysis of Vulnerabilities and Provision of Advanced Security Solutions for Communication Protocols in Air Traffic Control Networks**

The research focuses on cybersecurity challenges in critical aviation communication systems and proposes a multi-layer security architecture for improving the resilience of ATC networks.

---

# Citation

If you use this project or its implementation concepts in academic work, please cite the associated research paper:

```text
Rashidi, Amir Hossein.
"Analysis of Vulnerabilities and Provision of Advanced Security Solutions
for Communication Protocols in Air Traffic Control Networks."
Islamic Azad University, Tehran Central Branch.
```

---

# Disclaimer

This project is intended for **research, education, simulation, and cybersecurity experimentation in controlled environments**.

It does not interact with real aircraft, operational ATC systems, aviation communication infrastructure, or real RF channels.

Attack modules represent simulated cybersecurity scenarios and should only be used in authorized laboratory or research environments.

---


## Author

**Amir Hossein Rashidi**

Computer Engineering — Computer Networks
Islamic Azad University, Tehran Central Branch

**Research Focus:**
Air Traffic Control (ATC) Cybersecurity · Aviation Network Security · ADS-B Security · Intrusion Detection Systems · Post-Quantum Security

---

## Project Status

**Version:** `3.0`
**Type:** Research Prototype / Simulation
**Platform:** Python Desktop Application
**Primary Domain:** Aviation Cybersecurity / ATC Security
