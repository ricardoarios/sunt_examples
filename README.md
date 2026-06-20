# SUNT Examples

Visualization and demand forecasting examples for public transportation using the **SUNT** dataset (Salvador Urban Network of Transportation).

The dataset integrates AFC (fare collection), AVL (vehicle GPS), LTI (trip information), and GTFS data from Salvador/BA buses.

**Dataset paper:** Ferreira et al., *"SUNT: A multimodal urban public transportation dataset"*, Scientific Data, Nature (2025).  
**DOI:** [s41597-025-05674-6](https://www.nature.com/articles/s41597-025-05674-6)

---

## Script structure

Each script is self-contained and writes its results to `outputs/<topic>/`.

| Script | Model / Topic |
| --- | --- |
| `01_viz_timeseries.py` | Time series visualization (daily profiles, heatmap, seasonality, moving average) |
| `02_viz_graphs.py` | Network graph visualization (top-20 stops, centrality, interactive Folium map) |
| `03_forecast_sarima.py` | Univariate SARIMA with automatic order selection via `pmdarima.auto_arima` |
| `04_forecast_lstm.py` | Multivariate stacked LSTM (all N stops simultaneously) |
| `05_forecast_gru.py` | GRU — same architecture as LSTM with GRU cells |
| `06_forecast_transformer.py` | Encoder-only Transformer with positional encoding |
| `07_forecast_chronos.py` | Chronos (Amazon) — zero-shot foundation model, no training required |
| `08_forecast_gcn.py` | Pure spatial GCN — baseline for graph models |
| `09_forecast_gnn.py` | T-GCN — spatial GCN + temporal GRU (Zhao et al., 2020) |
| `10_forecast_gat.py` | T-GAT — spatial GAT + temporal GRU (Veličković et al., 2018) |

---

## Installation

**Notes:**

- `torch-geometric` requires a separate installation compatible with the installed PyTorch version — see [pytorch-geometric.readthedocs.io](https://pytorch-geometric.readthedocs.io/en/latest/install/installation.html). Scripts 08, 09, and 10 fall back to a custom implementation if PyG is not available.
- `chronos-forecasting` requires Python 3.12+.

Bellow instrunctions to instal overall dependencies using pip or uv.

### UV

To install dependencies using uv, run:

```bash
uv sync
```

To run any scripts of this tutorial, run:

```bash
uv run <file_script>.py
```

### Pip

To install dependencies using pip, run:

```bash
pip install -r requirements.txt
```

To run any scripts of this tutorial, run:

```bash
python <file_script>.py
```

---

## How to run

```bash
python 01_viz_timeseries.py
python 03_forecast_sarima.py
python 10_forecast_gat.py
# etc.
```

Scripts automatically download and cache data to `~/.cache/sunt_dataset/`. On the first run, wait for the Parquet files to download from HuggingFace.

---

## Data (`utils/data_loader.py`)

The `utils` module centralizes dataset access via the `suntdataset` package (PyPI) or directly from HuggingFace (`source="hgface"`).

| Function | Returns |
| --- | --- |
| `load_timeseries(freq, top_n, ...)` | `(T × N)` matrix of boardings per stop — primary input for deep learning models |
| `load_boarding(...)` | Raw boarding events |
| `load_alighting(...)` | Estimated alighting events |
| `load_od(...)` | Origin-Destination table (loading per stop/trip) |
| `load_gtfs(table)` | Static GTFS tables: `stops`, `trips`, `routes`, `shapes`, `agency` |
| `prepare_sequences(ts, input_len, horizon)` | Sliding window → `{X_train, y_val, X_test, scaler, …}` |
| `build_graph_from_od(od)` | `nx.DiGraph` of flows between consecutive stops |

**Available day types:** `"all"`, `"workdays"`, `"saturdays"`, `"sundays"`

---

## Graph models (08–10)

All three build the network graph from OD data:

- **Nodes** = bus stops (top N by boarding volume)
- **Edges** = consecutive stops on the same trip, weighted by total passengers

| Model | Spatial component | Temporal component |
| --- | --- | --- |
| GCN (08) | GCNConv — fixed weights from normalized adjacency | — (INPUT_LEN as direct features) |
| T-GCN (09) | GCNConv — fixed weights | GRU |
| T-GAT (10) | GATConv — **learned attention** per edge | GRU |

T-GAT also generates `gat_attention.png` (custom implementation): an N×N heatmap showing which stop pairs the model learned to prioritize.

---

## Common hyperparameters (deep learning)

| Parameter | Default value |
| --- | --- |
| `INPUT_LEN` | 72 (3 hourly days) |
| `HORIZON` | 24 (1-day-ahead forecast) |
| `FREQ` | `"1h"` |
| `EPOCHS` | 50–60 |
| `DEVICE` | CUDA if available, otherwise CPU |
| `SEED` | 42 |

Reported metrics: **MAE**, **RMSE**, **MAPE** on original-scale values (passengers/hour).

---

## Generated outputs

```bash
outputs/
  viz_timeseries/     daily profiles, heatmap, seasonality, moving average
  viz_graphs/         top-20 graph, centrality, interactive map (.html)
  sarima/             ACF/PACF, forecast with confidence interval
  lstm/               training curves, forecast, lstm_best.pt
  gru/                training curves, forecast, gru_best.pt
  transformer/        forecast, transformer_best.pt
  chronos/            zero-shot forecast
  gcn/                forecast, MAE per node, gcn_best.pt
  gnn/                forecast, MAE per node, tgcn_best.pt
  gat/                forecast, MAE per node, attention heatmap, gat_best.pt
```
