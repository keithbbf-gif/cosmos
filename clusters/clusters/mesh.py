"""Projects, six shortcuts, clusters, subclusters, manager, and HERO PACKS.

A cluster holds agents, agents and clusters, or only subclusters.
A manager session is optional. A pack is rules, skills, wrappers, and
environments on an agent, a cluster, or both.
A bad call raises Refuse.
A subcluster member requires the child cluster's parent_id to be this cluster.
"""

from __future__ import annotations

from clusters.models import MEMBER_KINDS, PACK_SCOPES, SHORTCUT_CAP
from clusters.refuse import Refuse, guard_path
from clusters.store import Store, new_id


def create_project(store: Store, *, name: str, root: str) -> dict:
    """Open a project. An empty name is a PROJECT refusal."""
    if not name.strip():
        raise Refuse("PROJECT", "name")
    guard_path(root)
    project_id = new_id("prj")
    body = {
        "id": project_id,
        "op": "open",
        "name": name.strip(),
        "root": root,
        "shortcut": 0,
    }
    store.append("project", body)
    return dict(store.view("project")[project_id])


def list_projects(store: Store) -> list[dict]:
    """List projects, six shortcut slots ahead of the unpinned rows."""
    rows = list(store.view("project").values())
    rows.sort(key=lambda row: (row.get("shortcut") or 99, row["id"]))
    return rows


def get_project(store: Store, project_id: str) -> dict:
    """Return one project. A missing id is a PROJECT refusal."""
    row = store.view("project").get(project_id)
    if row is None:
        raise Refuse("PROJECT", project_id)
    return dict(row)


def set_project_shortcut(store: Store, project_id: str, slot: int) -> dict:
    """Pin a project on one of six shortcuts, or clear it with slot 0."""
    get_project(store, project_id)
    if slot != 0 and slot not in range(1, SHORTCUT_CAP + 1):
        raise Refuse("SHORTCUT", str(slot))
    if slot:
        for other in store.view("project").values():
            if other["id"] != project_id and other.get("shortcut") == slot:
                cleared = dict(other)
                cleared["op"] = "shortcut"
                cleared["shortcut"] = 0
                store.append("project", _strip(cleared))
    current = get_project(store, project_id)
    body = dict(current)
    body["op"] = "shortcut"
    body["shortcut"] = slot
    store.append("project", _strip(body))
    return get_project(store, project_id)


def create_cluster(store: Store, *, name: str, project_id: str, parent_id: str = "") -> dict:
    """Open a cluster or subcluster. A parent on another project is refused."""
    if not name.strip():
        raise Refuse("CLUSTER", "name")
    get_project(store, project_id)
    if parent_id:
        parent = store.view("cluster").get(parent_id)
        if parent is None:
            raise Refuse("CLUSTER", parent_id)
        if parent.get("project_id") != project_id:
            raise Refuse("CLUSTER", "parent project")
    cluster_id = new_id("clu")
    body = {
        "id": cluster_id,
        "op": "open",
        "name": name.strip(),
        "project_id": project_id,
        "parent_id": parent_id,
        "manager_id": "",
        "members": [],
    }
    store.append("cluster", body)
    return dict(store.view("cluster")[cluster_id])


def add_member(store: Store, cluster_id: str, *, member_kind: str, member_id: str) -> dict:
    """Add an agent or a subcluster. The child cluster's parent_id must be this cluster."""
    if member_kind not in MEMBER_KINDS:
        raise Refuse("MEMBER", member_kind)
    current = _cluster(store, cluster_id)
    if member_kind == "agent":
        session = store.view("session").get(member_id)
        if session is None:
            raise Refuse("SESSION", member_id)
        if session.get("project_id") != current["project_id"]:
            raise Refuse("MEMBER", "project")
    else:
        child = store.view("cluster").get(member_id)
        if child is None or child.get("parent_id") != cluster_id:
            raise Refuse("CLUSTER", "subcluster must name this parent")
    members = list(current.get("members") or [])
    item = {"kind": member_kind, "id": member_id}
    if item not in members:
        members.append(item)
    body = dict(current)
    body["op"] = "member"
    body["members"] = members
    store.append("cluster", _strip(body))
    return _cluster(store, cluster_id)


def set_manager(store: Store, cluster_id: str, session_id: str) -> dict:
    """Set the optional manager. A non-coordinator session is a MANAGER refusal."""
    current = _cluster(store, cluster_id)
    session = store.view("session").get(session_id)
    if session is None:
        raise Refuse("SESSION", session_id)
    if session.get("role") not in ("coordinator", "global_coordinator"):
        raise Refuse("MANAGER", "manager is a coordinator session")
    if session.get("project_id") != current["project_id"] and session.get("role") != "global_coordinator":
        raise Refuse("MANAGER", "project")
    body = dict(current)
    body["op"] = "manager"
    body["manager_id"] = session_id
    store.append("cluster", _strip(body))
    return _cluster(store, cluster_id)


def attach_pack(
    store: Store,
    *,
    scope: str,
    target_id: str,
    rules: list | None = None,
    skills: list | None = None,
    wrappers: list | None = None,
    environments: list | None = None,
) -> dict:
    """Attach a HERO PACK of rules, skills, wrappers, and environments."""
    if scope not in PACK_SCOPES:
        raise Refuse("PACK", scope)
    if scope in ("agent", "both") and target_id not in store.view("session"):
        raise Refuse("SESSION", target_id)
    if scope == "cluster" and target_id not in store.view("cluster"):
        raise Refuse("CLUSTER", target_id)
    pack_id = new_id("pak")
    body = {
        "id": pack_id,
        "op": "attach",
        "scope": scope,
        "target_id": target_id,
        "rules": _strings(rules),
        "skills": _strings(skills),
        "wrappers": _strings(wrappers),
        "environments": _strings(environments),
    }
    store.append("pack", body)
    return dict(store.view("pack")[pack_id])


def list_clusters(store: Store, project_id: str = "") -> list[dict]:
    """List clusters, optionally for one project."""
    rows = [dict(row) for row in store.view("cluster").values()]
    if project_id:
        rows = [row for row in rows if row["project_id"] == project_id]
    rows.sort(key=lambda row: row["id"])
    return rows


def get_cluster(store: Store, cluster_id: str) -> dict:
    """Return one cluster. A missing id is a CLUSTER refusal."""
    return _cluster(store, cluster_id)


def _cluster(store: Store, cluster_id: str) -> dict:
    row = store.view("cluster").get(cluster_id)
    if row is None:
        raise Refuse("CLUSTER", cluster_id)
    return dict(row)


def _strings(values: list | None) -> list[str]:
    if not values:
        return []
    out: list[str] = []
    for item in values:
        text = str(item).strip()
        if "\n" in text or len(text) > 240:
            raise Refuse("PACK", "entries are short single lines")
        if text:
            out.append(text)
    return out


def _strip(body: dict) -> dict:
    return {key: value for key, value in body.items() if not key.startswith("_")}
