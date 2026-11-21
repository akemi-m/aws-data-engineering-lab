
import csv
from pathlib import Path

# Localiza a pasta do projeto independentemente do terminal.
PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_DIR / "data" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

datasets = {
    "clientes": [
        {"cliente_id": 1, "nome": "Ana", "cidade": "Sao Paulo"},
        {"cliente_id": 2, "nome": "Bruno", "cidade": "Campinas"},
        {"cliente_id": 3, "nome": "Carla", "cidade": "Santos"},
        {"cliente_id": 4, "nome": "Diego", "cidade": "Sorocaba"},
    ],
    "produtos": [
        {"produto_id": 101, "nome": "Notebook", "categoria": "Eletronicos", "preco": 3500.00},
        {"produto_id": 102, "nome": "Mouse", "categoria": "Eletronicos", "preco": 80.00},
        {"produto_id": 103, "nome": "Cadeira", "categoria": "Escritorio", "preco": 900.00},
        {"produto_id": 104, "nome": "Mesa", "categoria": "Escritorio", "preco": 650.00},
    ],
    "pedidos": [
        {"pedido_id": 1001, "cliente_id": 1, "produto_id": 101, "quantidade": 1, "data_pedido": "2026-11-01", "status": "CONCLUIDO"},
        {"pedido_id": 1002, "cliente_id": 2, "produto_id": 102, "quantidade": 2, "data_pedido": "2026-11-02", "status": "CONCLUIDO"},
        {"pedido_id": 1003, "cliente_id": 1, "produto_id": 103, "quantidade": 1, "data_pedido": "2026-11-03", "status": "CANCELADO"},
        {"pedido_id": 1004, "cliente_id": 3, "produto_id": 104, "quantidade": 1, "data_pedido": "2026-11-04", "status": "CONCLUIDO"},
        {"pedido_id": 1005, "cliente_id": 4, "produto_id": 102, "quantidade": 3, "data_pedido": "2026-11-05", "status": "CONCLUIDO"},
        {"pedido_id": 1006, "cliente_id": 2, "produto_id": 101, "quantidade": 1, "data_pedido": "2026-11-06", "status": "CONCLUIDO"},
    ],
    "pagamentos": [
        {"pagamento_id": 501, "pedido_id": 1001, "metodo": "PIX", "valor": 3500.00, "status": "APROVADO"},
        {"pagamento_id": 502, "pedido_id": 1002, "metodo": "CARTAO", "valor": 160.00, "status": "APROVADO"},
        {"pagamento_id": 503, "pedido_id": 1003, "metodo": "PIX", "valor": 900.00, "status": "ESTORNADO"},
        {"pagamento_id": 504, "pedido_id": 1004, "metodo": "CARTAO", "valor": 650.00, "status": "APROVADO"},
        {"pagamento_id": 505, "pedido_id": 1005, "metodo": "PIX", "valor": 240.00, "status": "APROVADO"},
        {"pagamento_id": 506, "pedido_id": 1006, "metodo": "CARTAO", "valor": 3500.00, "status": "APROVADO"},
    ],
}

for name, rows in datasets.items():
    file_path = OUTPUT_DIR / f"{name}.csv"

    with file_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Gerado: {file_path} ({len(rows)} registros)")
