import json
import hashlib
import datetime as dt
from datetime import timezone
from typing import Any
from neo4j import GraphDatabase, Driver


def canonical_sig(evidence: dict[str, Any]) -> str:
    data = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(data.encode()).hexdigest()


class OAOBRepo:
    def __init__(self, driver: Driver) -> None:
        self._driver = driver

    def ingest_oa(
            self,
            oa_key: str,
            attrs: dict[str, Any],
            hint: dict[str, Any]
            ):
        """
        - Develops a unique hint signature.
        - Gets datetime (for purging pending relationships after some time).
        - Builds concrete oa with attributes (node oa is known.)
        - Builds a SymbolicNode for some hypothetical ob.
        - Adds the information which we believe makes it exist.
        - Creates a pending binding between oa and a hypothetical ob.
        """
        sig = canonical_sig(hint)
        now = dt.datetime.now(timezone.utc).isoformat()
        query = """
        MERGE (oa:OA {key:$oa_key})
        SET oa += $attrs
        WITH oa
        MERGE (h:SymbolicNode {sig:$sig})
        ON CREATE SET h += $hint, h.associated=$now
        MERGE (oa)-[:PENDING {sig:$sig, associated:$now}]-(h)
        """
        self.execute(
            query,
            oa_key=oa_key,
            attrs=attrs,
            sig=sig,
            hint=hint,
            now=now
        )

    def ingest_ob(self, ob_key: str, attrs: dict[str, Any]):
        """
        - Creates some node ob which we know in this context concretely exists.
        - Completes naïve search for props i.e. name for pending bindings.
        - If a match is made a key is assigned to ob.
        - Check for where a exists between some oa and h.
        - If exists delete h and a.

        Idea for using direct match signatures:

        sig = canonical_sig(evidence) if evidence else None
        MATCH (h:SymbolicNode {sig:$sig})
        OPTIONAL MATCH (oa:OA)-[a:PENDING {sig:$sig}]-(h)
        """
        query = "MERGE (ob:OB {key:$key}) SET ob += $attrs"
        self._run(query, key=ob_key, attrs=attrs)

        promotion = """
        MATCH (h:SymbolicNode)
        WHERE h.name = $name
        WITH h
        OPTIONAL MATCH (oa:OA)-[a:PENDING]-(h)
        MERGE (ob:OB {key:$key})
        WITH oa, ob, a, h
        FOREACH (
            _ IN CASE WHEN a IS NULL THEN [] ELSE [1] END |
            MERGE (oa)-[:CONFIRMED]-(ob) DELETE a
        )
        WITH h
        WHERE NOT (h)-[:PENDING]-()
        DETACH DELETE h
        """
        self.execute(promotion, key=ob_key, name=attrs["name"])

    def execute(self, cypher: str, **params):
        with self._driver.session() as session:
            session.execute_write(lambda tx: tx.run(cypher, **params))


if __name__ == "__main__":
    drv = GraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "password")
    )
    repo = OAOBRepo(drv)

    repo.ingest_oa(
        oa_key="Statue of Liberty",
        attrs={"desc": "Landmark in New York City"},
        hint={"name": "United States of America", "kind": "Country"}
    )

    repo.ingest_ob(
        ob_key="USA",
        attrs={"name": "United States of America", "formed": "1768"}
    )

    print("Run `MATCH (oa)-[r]->(ob) RETURN oa, r, ob` to verify promotion.")
