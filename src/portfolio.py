import os

# Hardcoded positions {ticker: (PRU, qty)}
# Fallback when no DATABASE_URL, and source for src/seed.py
PORTEFEUILLE = {
    "AI.PA": (150.87, 11),
    "ASML.AS": (1189.12, 1),
    "DCAM.PA": (5.91, 600),
    "ASM.AS": (717.17, 1),
    "PSP5.PA": (55.59, 24),
    "SU.PA": (249.07, 7),
    "MC.PA": (540.32, 1),
    "RI.PA": (80.44, 5),
    "ACA.PA": (18.30, 21),
    "STMPA.PA": (26.09, 10),
    "EL.PA": (247.60, 2),
    "ITP.PA": (25.33, 10),
    "FDJU.PA": (25.61, 10),
    "SAN.PA": (81.10, 3),
    "TTE.PA": (63.08, 3),
    "DSY.PA": (18.13, 10),
    "EDEN.PA": (17.83, 10),
    "BESI.AS": (165.27, 1),
    "OVH.PA": (15.28, 12),
    "CA.PA": (14.94, 10),
    "ALO.PA": (21.11, 10),
    "UBI.PA": (4.10, 51),
    "ALRIB.PA": (9.55, 15),
}


def connect():
    # psycopg imported here so the report still runs without it when no db is used
    import psycopg

    return psycopg.connect(os.environ["DATABASE_URL"])


def load_positions(conn):
    """Positions {ticker: (PRU, qty)} rebuilt from the transactions table.

    PRU is the weighted average cost, fees included in buys.
    A sell lowers the qty but keeps the PRU; it resets once the position is closed.
    """
    rows = conn.execute(
        "SELECT ticker, qty, price, fees FROM transactions ORDER BY date, id"
    ).fetchall()

    book = {}  # ticker -> [qty, cost]
    for ticker, qty, price, fees in rows:
        qty, price, fees = float(qty), float(price), float(fees)
        pos = book.setdefault(ticker, [0.0, 0.0])
        if qty > 0:
            pos[1] += qty * price + fees
        elif pos[0] > 0:
            pos[1] *= (pos[0] + qty) / pos[0]
        pos[0] += qty
        if pos[0] <= 1e-9:
            book[ticker] = [0.0, 0.0]

    return {
        ticker: (cost / qty, int(qty) if qty.is_integer() else qty)
        for ticker, (qty, cost) in book.items()
        if qty > 1e-9
    }
