from lnbits.db import Database


async def m001_initial(db: Database):
    await db.execute(
        f"""
        CREATE TABLE IF NOT EXISTS tipjar.TipJars (
            id {db.serial_primary_key},
            name TEXT NOT NULL,
            wallet TEXT NOT NULL,
            onchain TEXT,
            webhook TEXT
        );
        """
    )

    await db.execute(
        f"""
        CREATE TABLE IF NOT EXISTS tipjar.Tips (
            id TEXT PRIMARY KEY,
            wallet TEXT NOT NULL,
            name TEXT NOT NULL,
            message TEXT NOT NULL,
            sats {db.big_int} NOT NULL,
            tipjar {db.big_int} NOT NULL,
            FOREIGN KEY(tipjar) REFERENCES {db.references_schema}TipJars(id)
        );
        """
    )


async def m002_add_onchain_limit(db: Database):
    await db.execute(
        """
        ALTER TABLE tipjar.TipJars ADD COLUMN onchain_limit INTEGER;
        """
    )


async def m003_tipjar_id_string(db: Database):
    await db.execute(
        """
        ALTER TABLE tipjar.TipJars ALTER COLUMN id TYPE TEXT;
        """
    )
    await db.execute(
        """
        ALTER TABLE tipjar.Tips ALTER COLUMN tipjar TYPE TEXT;
        """
    )
