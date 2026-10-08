"""Facade the local HTTP handler calls. Rules live in the modules, not here."""

from __future__ import annotations

from clusters import (
    allowance,
    attach,
    bind,
    board,
    catalog,
    changes,
    confirm,
    conflict,
    coordinators,
    credroute,
    doorcap,
    doorid,
    gitx,
    harness,
    headless,
    history,
    hostnote,
    instruct,
    isolate,
    lane,
    link,
    marks,
    mesh,
    meter,
    notice,
    perms,
    policy,
    presets,
    qshape,
    quota,
    relay,
    room,
    seatflag,
    sessions,
    skills,
    spend,
    subtasks,
    thread,
    toolperm,
)
from clusters import (
    seen as seen_mod,
)
from clusters.models import FEATURES
from clusters.store import Store

__version__ = "0.1.0"


class Console:
    def __init__(self, root: str) -> None:
        self.store = Store(root)

    def health(self) -> dict:
        return {"ok": True, "service": "clusters", "version": __version__}

    def features(self) -> dict:
        return {"features": list(FEATURES)}

    def create_project(self, name: str, root: str) -> dict:
        return mesh.create_project(self.store, name=name, root=root)

    def list_projects(self) -> list:
        return mesh.list_projects(self.store)

    def shortcut(self, project_id: str, slot: int) -> dict:
        return mesh.set_project_shortcut(self.store, project_id, int(slot))

    def create_cluster(self, name: str, project_id: str, parent_id: str = "") -> dict:
        return mesh.create_cluster(self.store, name=name, project_id=project_id, parent_id=parent_id)

    def list_clusters(self, project_id: str = "") -> list:
        return mesh.list_clusters(self.store, project_id)

    def add_member(self, cluster_id: str, member_kind: str, member_id: str) -> dict:
        return mesh.add_member(self.store, cluster_id, member_kind=member_kind, member_id=member_id)

    def set_manager(self, cluster_id: str, session_id: str) -> dict:
        return mesh.set_manager(self.store, cluster_id, session_id)

    def attach_pack(
        self,
        scope: str,
        target_id: str,
        rules: list | None = None,
        skills: list | None = None,
        wrappers: list | None = None,
        environments: list | None = None,
    ) -> dict:
        return mesh.attach_pack(
            self.store,
            scope=scope,
            target_id=target_id,
            rules=rules,
            skills=skills,
            wrappers=wrappers,
            environments=environments,
        )

    def open_session(
        self,
        project_id: str,
        door: str,
        hero: str = "",
        model: str = "",
        task: str = "",
        role: str = "worker",
        account_id: str = "",
        cluster_id: str = "",
        parent_id: str = "",
        title: str = "",
    ) -> dict:
        return sessions.open_session(
            self.store,
            project_id=project_id,
            door=door,
            hero=hero,
            model=model,
            task=task,
            role=role,
            account_id=account_id,
            cluster_id=cluster_id,
            parent_id=parent_id,
            title=title,
        )

    def list_sessions(self, project_id: str = "") -> list:
        return sessions.list_sessions(self.store, project_id)

    def set_status(self, session_id: str, status: str, evidence: dict | None = None) -> dict:
        return sessions.set_status(self.store, session_id, status, evidence=evidence)

    def set_title(self, session_id: str, title: str, evidence: dict | None = None) -> dict:
        return sessions.set_title(self.store, session_id, title, evidence=evidence)

    def put_layout(self, session_id: str, view: str, bounds: dict) -> dict:
        return sessions.put_layout(self.store, session_id, view=view, bounds=bounds or {})

    def close_session(self, session_id: str, confirm: bool = False) -> dict:
        return sessions.close_session(self.store, session_id, confirm=bool(confirm))

    def open_coordinator(self, scope: str, project_id: str, hero: str, door: str, model: str) -> dict:
        return coordinators.open_coordinator(
            self.store, scope=scope, project_id=project_id, hero=hero, door=door, model=model
        )

    def submit_goal(self, coordinator_id: str, text: str) -> dict:
        return coordinators.submit_goal(self.store, coordinator_id, text)

    def accept_plan(self, coordinator_id: str, plan: dict, evidence: dict | None = None) -> dict:
        return coordinators.accept_plan(self.store, coordinator_id, plan, evidence=evidence)

    def report(self, coordinator_id: str) -> dict:
        return coordinators.report(self.store, coordinator_id)

    def close_worker(self, coordinator_id: str, worker_id: str, confirm: bool = False) -> dict:
        return coordinators.close_worker(
            self.store, coordinator_id, worker_id, confirm=bool(confirm)
        )

    def ask_session(self, sender_id: str, target_id: str, question: str) -> dict:
        return coordinators.ask_session(
            self.store, sender_id=sender_id, target_id=target_id, question=question
        )

    def set_session_comms(self, enabled: bool) -> dict:
        return coordinators.set_session_comms(self.store, bool(enabled))

    def add_task(
        self,
        project_id: str,
        title: str,
        body: str = "",
        column: str = "pending",
        door: str = "",
        hero: str = "",
        model: str = "",
        labels: list | None = None,
        workspace: str = "",
    ) -> dict:
        return board.add_task(
            self.store,
            project_id=project_id,
            title=title,
            body=body,
            column=column,
            door=door,
            hero=hero,
            model=model,
            labels=labels,
            workspace=workspace,
        )

    def list_tasks(self, project_id: str = "") -> list:
        return board.list_tasks(self.store, project_id)

    def move_task(self, task_id: str, column: str, evidence: dict | None = None) -> dict:
        return board.move_task(self.store, task_id, column, evidence=evidence)

    def auto_tick(self, limit: int | None = None, project_id: str = "") -> dict:
        return board.auto_tick(self.store, limit=limit, project_id=project_id)

    def add_message(self, session_id: str, role: str, kind: str, body: str, resume_of: str = "") -> dict:
        return history.add_message(
            self.store, session_id=session_id, role=role, kind=kind, body=body, resume_of=resume_of
        )

    def search(self, query: str, project_id: str = "") -> list:
        return history.search(self.store, query, project_id=project_id)

    def resume_pointer(self, session_id: str) -> dict:
        return history.resume_pointer(self.store, session_id)

    def record_change(self, session_id: str, path: str, before: str, after: str, diff: str) -> dict:
        return changes.record_change(
            self.store, session_id=session_id, path=path, before=before, after=after, diff=diff
        )

    def list_changes(self, session_id: str = "") -> list:
        return changes.list_changes(self.store, session_id)

    def plan_worktree(self, session_id: str, repo: str) -> dict:
        return changes.plan_worktree(self.store, session_id=session_id, repo=repo)

    def propose_commit(self, session_id: str, summary: str) -> dict:
        return changes.propose_commit(self.store, session_id=session_id, summary=summary)

    def request_push(self, session_id: str, branch: str, confirmed: bool = False) -> dict:
        return changes.request_push(
            self.store, session_id=session_id, branch=branch, confirmed=bool(confirmed)
        )

    def check_command(self, command: str, turbo: bool = False, branch: str = "") -> dict:
        return policy.check_command(self.store, command=command, turbo=bool(turbo), branch=branch)

    def set_limits(self, allow: list | None = None, deny: list | None = None) -> dict:
        return policy.set_limits(self.store, allow=allow, deny=deny)

    def set_budget(
        self,
        provider: str,
        daily_cap_usd: float,
        daily_cap_tokens: int = 0,
        mode: str = "cap",
        on_limit: str = "pause",
        window_days: int = 1,
        day_index: int = 0,
    ) -> dict:
        return spend.set_budget(
            self.store,
            provider=provider,
            daily_cap_usd=float(daily_cap_usd),
            daily_cap_tokens=int(daily_cap_tokens),
            mode=mode,
            on_limit=on_limit,
            window_days=int(window_days),
            day_index=int(day_index),
        )

    def observe_spend(
        self,
        provider: str,
        usd: float,
        tokens: int = 0,
        source: str = "",
        observed: str = "",
        day_index: int = 0,
    ) -> dict:
        return spend.observe(
            self.store,
            provider=provider,
            usd=float(usd),
            tokens=int(tokens),
            source=source,
            observed=observed,
            day_index=int(day_index),
        )

    def bump_today(self, provider: str) -> dict:
        return spend.bump_today(self.store, provider=provider)

    def check_spend(self, provider: str, usd: float = 0, tokens: int = 0) -> dict:
        return spend.check(self.store, provider=provider, usd=float(usd), tokens=int(tokens))

    def spend_report(self) -> list:
        return spend.report(self.store)

    def list_doors(self) -> list:
        return catalog.list_doors()

    def add_account(self, provider: str, label: str, profile_dir: str) -> dict:
        return catalog.add_account(
            self.store, provider=provider, label=label, profile_dir=profile_dir
        )

    def bind_account(self, session_id: str, account_id: str) -> dict:
        return catalog.bind_account(self.store, session_id, account_id)

    def set_mcp(self, project_id: str, server_id: str, enabled: bool) -> dict:
        return catalog.set_mcp(
            self.store, project_id=project_id, server_id=server_id, enabled=bool(enabled)
        )

    def enable_all_mcp(self, project_id: str) -> dict:
        return catalog.enable_all_mcp(self.store, project_id=project_id)

    def list_mcp(self, project_id: str) -> list:
        return catalog.list_mcp(self.store, project_id)

    def add_shortcut(self, kind: str, binding: str, target: str) -> dict:
        return catalog.add_shortcut(self.store, kind=kind, binding=binding, target=target)

    def list_shortcuts(self) -> list:
        return catalog.list_shortcuts(self.store)

    def pair_mobile(self) -> dict:
        return catalog.pair_mobile(self.store)

    def set_desktop(self, online: bool) -> dict:
        return catalog.set_desktop(self.store, online=bool(online))

    def mobile_message(self, token: str, session_id: str, body: str) -> dict:
        return catalog.mobile_message(self.store, token=token, session_id=session_id, body=body)

    def list_notifications(self) -> list:
        return catalog.list_notes(self.store)

    def see_notification(self, note_id: str) -> dict:
        return catalog.see(self.store, note_id)

    def plan_harness(
        self,
        hero: str,
        task: str,
        where: str,
        via: str = "cosmos-code",
        execute: bool = False,
    ) -> dict:
        return harness.plan_seat(hero, task, where, via=via, execute=bool(execute))

    # P1. Category allow never overrides a hard refusal from policy.check_command.
    def set_matrix(
        self,
        file: str = "ask",
        shell: str = "ask",
        git: str = "ask",
        network: str = "ask",
        mcp: str = "ask",
    ) -> dict:
        return perms.set_matrix(
            self.store, file=file, shell=shell, git=git, network=network, mcp=mcp,
        )

    def decide(self, category: str, command: str, turbo: bool = False) -> dict:
        return perms.decide(
            self.store, category=category, command=command, turbo=bool(turbo),
        )

    # P5. Verified finished moves in-progress cards to in_testing. It does not complete them.
    def link_status(
        self,
        session_id: str,
        status: str,
        evidence: dict | None = None,
        detail: str = "",
    ) -> dict:
        return link.on_status(
            self.store, session_id, status, evidence=evidence, detail=detail,
        )

    # P12. A skill row is a path flag. The file is not read.
    def enable_skill(self, project_id: str, path: str, enabled: bool = True) -> dict:
        return skills.enable_skill(
            self.store, project_id=project_id, path=path, enabled=bool(enabled),
        )

    def list_skills(self, project_id: str = "") -> list:
        return skills.list_skills(self.store, project_id)

    def skill_pack(self, project_id: str = "") -> list:
        return skills.skill_for_pack(self.store, project_id)

    # P13. An unmeasured quota figure pauses. It does not reduce the allowance.
    def set_quota_window(
        self,
        provider: str,
        limit_usd: float,
        period_seconds: int,
        resets_at: float,
        source: str,
        observed: str,
    ) -> dict:
        return quota.set_window(
            self.store,
            provider=provider,
            limit_usd=float(limit_usd),
            period_seconds=int(period_seconds),
            resets_at=float(resets_at),
            source=source,
            observed=observed,
        )

    def mark_quota_used(
        self, provider: str, used_usd: float, source: str, observed: str,
    ) -> dict:
        return quota.mark_used(
            self.store,
            provider=provider,
            used_usd=float(used_usd),
            source=source,
            observed=observed,
        )

    def quota_prorata(self, provider: str, now: float) -> dict:
        return quota.prorata(self.store, provider=provider, now=float(now))

    # P7–P9. Messages and handoff. This does not open a worker for small work.
    def send_worker(
        self, coordinator_id: str, worker_id: str, text: str, kind: str,
    ) -> dict:
        return relay.send_worker(
            self.store,
            coordinator_id=coordinator_id,
            worker_id=worker_id,
            text=text,
            kind=kind,
        )

    def keep_small(self, coordinator_id: str, text: str) -> dict:
        return relay.keep_small(self.store, coordinator_id=coordinator_id, text=text)

    def delegate_project(
        self,
        global_id: str,
        project_id: str,
        text: str,
        door: str,
        hero: str,
        model: str,
    ) -> dict:
        return relay.delegate_project(
            self.store,
            global_id=global_id,
            project_id=project_id,
            text=text,
            door=door,
            hero=hero,
            model=model,
        )

    # P14. Mode is stored. An unknown mode for that door refuses.
    def set_mode(self, session_id: str, mode: str) -> dict:
        return room.set_mode(self.store, session_id, mode)

    # P15. Cancel is an intent row. executed and killed stay false.
    def cancel_session(self, session_id: str) -> dict:
        return room.cancel(self.store, session_id)

    # P16. Follow lists sessions only while the desktop is online and the token hashes.
    def follow_mobile(self, token: str) -> dict:
        return room.follow(self.store, token=token)

    # P17. Seeds the default key map once. It does not replace bindings already stored.
    def seed_keys(self) -> dict:
        return room.seed_keys(self.store)

    # P3–P4. Queue only. auto_tick is what starts a session, and it does not execute.
    def set_lane_defaults(
        self,
        project_id: str,
        door: str,
        hero: str = "",
        model: str = "",
        reasoning: str = "medium",
        permission: str = "default",
        workspace: str = "worktree",
    ) -> dict:
        return lane.set_defaults(
            self.store,
            project_id=project_id,
            door=door,
            hero=hero,
            model=model,
            reasoning=reasoning,
            permission=permission,
            workspace=workspace,
        )

    def queue_drag(self, task_id: str) -> dict:
        return lane.queue_drag(self.store, task_id)

    def queue_lightning(
        self,
        task_id: str,
        door: str = "",
        hero: str = "",
        model: str = "",
        reasoning: str = "",
        permission: str = "",
        workspace: str = "",
    ) -> dict:
        return lane.queue_lightning(
            self.store,
            task_id,
            door=door,
            hero=hero,
            model=model,
            reasoning=reasoning,
            permission=permission,
            workspace=workspace,
        )

    def queue_new(
        self,
        project_id: str,
        title: str,
        body: str = "",
        door: str = "",
        hero: str = "",
        model: str = "",
        reasoning: str = "",
        permission: str = "",
        workspace: str = "",
        labels: list | None = None,
    ) -> dict:
        return lane.queue_new(
            self.store,
            project_id=project_id,
            title=title,
            body=body,
            door=door,
            hero=hero,
            model=model,
            reasoning=reasoning,
            permission=permission,
            workspace=workspace,
            labels=labels,
        )

    # P2. Names a git guard. A refused op is not run.
    def classify_git(self, command: str) -> dict:
        return gitx.classify(command)

    # P10. Without verified commit-text evidence the summary is the recorded diff.
    def propose_message(
        self, session_id: str, evidence: dict | None = None, style: str = "detailed",
    ) -> dict:
        return gitx.propose_message(
            self.store, session_id=session_id, evidence=evidence, style=style,
        )

    # P11. A review bundle is stored. pr, pushed, and executed stay false.
    def propose_review(self, session_id: str, summary: str) -> dict:
        return gitx.propose_review(self.store, session_id=session_id, summary=summary)

    # Title history. A row exists only for a verified title that changed.
    def list_titles(self, session_id: str) -> list:
        return sessions.list_titles(self.store, session_id)

    # Subtasks stay one level deep. This does not move a card or open a session.
    def add_subtask(self, parent_id: str, title: str, body: str = "") -> dict:
        return subtasks.add_subtask(
            self.store, parent_id=parent_id, title=title, body=body,
        )

    def list_subtasks(self, parent_id: str) -> list:
        return subtasks.list_subtasks(self.store, parent_id)

    # Bookmarks point at a session or a message. The message body is not copied.
    def add_bookmark(self, session_id: str, message_id: str = "", note: str = "") -> dict:
        return marks.add_bookmark(
            self.store, session_id=session_id, message_id=message_id, note=note,
        )

    def hide_bookmark(self, bookmark_id: str) -> dict:
        return marks.hide_bookmark(self.store, bookmark_id)

    def list_bookmarks(self, session_id: str = "") -> list:
        return marks.list_bookmarks(self.store, session_id)

    # Both projections must allow. This call does not record spend or quota.
    def admit(
        self, provider: str, now: float, usd: float = 0, tokens: int = 0,
    ) -> dict:
        return allowance.admit(
            self.store, provider=provider, usd=usd, tokens=tokens, now=now,
        )

    # Git confirmation is an observation. confirmed is true only when evidence is VERIFIED.
    def record_confirm(
        self,
        session_id: str,
        branch: str,
        clean: bool,
        evidence: dict | None = None,
    ) -> dict:
        return confirm.record_confirm(
            self.store,
            session_id=session_id,
            branch=branch,
            clean=clean,
            evidence=evidence,
        )

    # Isolation intent. executed and git stay false. origin/main is a name, not a push.
    def plan_isolation(
        self,
        task_id: str,
        base_ref: str,
        share: str,
        workspace: str,
        why: str = "",
        paths: list | None = None,
    ) -> dict:
        return isolate.plan_isolation(
            self.store,
            task_id=task_id,
            base_ref=base_ref,
            share=share,
            workspace=workspace,
            why=why,
            paths=paths,
        )

    # Door and model stored on the seat. started stays false. grok.exe does not start.
    def bind_seat(self, session_id: str, door: str, model: str) -> dict:
        return bind.bind_seat(self.store, session_id=session_id, door=door, model=model)

    def get_binding(self, session_id: str) -> dict:
        return bind.get_binding(self.store, session_id)

    # Attention is a reason and the store clock. Nothing is sent.
    def note_attention(self, session_id: str, reason: str) -> dict:
        return notice.note_attention(self.store, session_id=session_id, reason=reason)

    def list_attention(self, session_id: str = "") -> list:
        return notice.list_attention(self.store, session_id)

    # Settling a thread does not close the session.
    def set_thread(self, session_id: str, state: str, until: float = 0) -> dict:
        return thread.set_thread(self.store, session_id=session_id, state=state, until=until)

    def get_thread(self, session_id: str) -> dict:
        return thread.get_thread(self.store, session_id)

    # Colour, icon, door, resume, and turbo are stored. Nothing launches.
    def set_preset(
        self,
        project_id: str,
        colour: str,
        icon: str,
        door: str,
        resume: bool = False,
        turbo: bool = False,
    ) -> dict:
        return presets.set_preset(
            self.store,
            project_id=project_id,
            colour=colour,
            icon=icon,
            door=door,
            resume=resume,
            turbo=turbo,
        )

    def get_preset(self, project_id: str) -> dict:
        return presets.get_preset(self.store, project_id)

    # Work style and image paths. The files are not read and the column stays put.
    def attach_task(
        self,
        task_id: str,
        work_style: str,
        style_text: str = "",
        images: list | None = None,
    ) -> dict:
        return attach.attach(
            self.store,
            task_id=task_id,
            work_style=work_style,
            style_text=style_text,
            images=images,
        )

    # A path stays unseen until the operator marks it. accepted stays false. No commit.
    def mark_seen(self, session_id: str, path: str, seen: bool = True) -> dict:
        return seen_mod.mark_seen(self.store, session_id=session_id, path=path, seen=seen)

    def review_paths(self, session_id: str) -> dict:
        return seen_mod.review_paths(self.store, session_id)

    # Instruction and MCP paths. The file is not read. Import does not write settings.
    def add_instruction(self, project_id: str, kind: str, path: str) -> dict:
        return instruct.add_instruction(
            self.store, project_id=project_id, kind=kind, path=path,
        )

    def set_import(self, project_id: str, result: str) -> dict:
        return instruct.set_import(self.store, project_id=project_id, result=result)

    def list_instructions(self, project_id: str = "") -> list:
        return instruct.list_instructions(self.store, project_id)

    # Provider conversation id. resume_claimed stays false. This does not resume.
    def set_door_id(self, session_id: str, conversation_id: str, home: str) -> dict:
        return doorid.set_door_id(
            self.store,
            session_id=session_id,
            conversation_id=conversation_id,
            home=home,
        )

    def get_door_id(self, session_id: str) -> dict:
        return doorid.get_door_id(self.store, session_id)

    # Login route and a path pointer. The file is not opened and no secret is stored.
    def set_route(self, session_id: str, route: str, path: str) -> dict:
        return credroute.set_route(
            self.store, session_id=session_id, route=route, path=path,
        )

    def get_route(self, session_id: str) -> dict:
        return credroute.get_route(self.store, session_id)

    # A named quota shape. Unmeasured pauses. This does not reduce spend.
    def set_shape(
        self,
        provider: str,
        shape: str,
        limit_label: str,
        source: str,
        observed: str,
    ) -> dict:
        return qshape.set_shape(
            self.store,
            provider=provider,
            shape=shape,
            limit_label=limit_label,
            source=source,
            observed=observed,
        )

    def shape_gate(self, provider: str, shape: str) -> dict:
        return qshape.shape_gate(self.store, provider=provider, shape=shape)

    # Mode and provider are stored. applied and started stay false. Nothing launches.
    def set_caps(
        self,
        session_id: str,
        mode: str,
        provider: str = "",
        subagents: bool = True,
        worktree: str = "",
        command_path: str = "",
    ) -> dict:
        return doorcap.set_caps(
            self.store,
            session_id=session_id,
            mode=mode,
            provider=provider,
            subagents=subagents,
            worktree=worktree,
            command_path=command_path,
        )

    def get_caps(self, session_id: str) -> dict:
        return doorcap.get_caps(self.store, session_id)

    # Host fact. probed stays false. Nothing is probed.
    def set_host(self, session_id: str, host: str, fact: str, enabled: bool) -> dict:
        return hostnote.set_host(
            self.store, session_id=session_id, host=host, fact=fact, enabled=enabled,
        )

    # Env name only. A secret-shaped name is refused and no value is stored.
    def set_env_name(self, session_id: str, name: str) -> dict:
        return hostnote.set_env_name(self.store, session_id=session_id, name=name)

    # Same-file conflict outcome. Git is not run and the path is not written.
    def record_conflict(self, session_id: str, path: str, outcome: str) -> dict:
        return conflict.record_conflict(
            self.store, session_id=session_id, path=path, outcome=outcome,
        )

    def list_conflicts(self, session_id: str = "") -> list:
        return conflict.list_conflicts(self.store, session_id)

    # One tool on one MCP server. A missing row stays ask. The tool is not called.
    def set_tool(self, project_id: str, server_id: str, tool: str, level: str) -> dict:
        return toolperm.set_tool(
            self.store,
            project_id=project_id,
            server_id=server_id,
            tool=tool,
            level=level,
        )

    def tool_level(self, project_id: str, server_id: str, tool: str) -> dict:
        return toolperm.tool_level(
            self.store, project_id=project_id, server_id=server_id, tool=tool,
        )

    # Headless intent. started and executed stay false. grok.exe does not start.
    def plan_headless(
        self,
        session_id: str,
        output_format: str = "plain",
        max_turns: int = 1,
        sandbox: str = "",
    ) -> dict:
        return headless.plan_headless(
            self.store,
            session_id=session_id,
            output_format=output_format,
            max_turns=max_turns,
            sandbox=sandbox,
        )

    def get_headless(self, session_id: str) -> dict:
        return headless.get_headless(self.store, session_id)

    # Channel, role, and updater path. written and fetched stay false.
    def set_seat_flags(
        self,
        session_id: str,
        channel: str = "stable",
        role: str = "",
        tool_search: bool = False,
        web_fetch: bool = False,
        hooks_off: bool = False,
        auto_update: bool = False,
        lock_path: str = "",
    ) -> dict:
        return seatflag.set_seat_flags(
            self.store,
            session_id=session_id,
            channel=channel,
            role=role,
            tool_search=tool_search,
            web_fetch=web_fetch,
            hooks_off=hooks_off,
            auto_update=auto_update,
            lock_path=lock_path,
        )

    def get_seat_flags(self, session_id: str) -> dict:
        return seatflag.get_seat_flags(self.store, session_id)

    # Usage reading. Empty is not unlimited. Logged-out is not stopped. Spend is not reduced.
    def set_meter(
        self,
        provider: str,
        reading: str,
        pool: str,
        auto_reload: bool = False,
        source: str = "",
        observed: str = "",
    ) -> dict:
        return meter.set_meter(
            self.store,
            provider=provider,
            reading=reading,
            pool=pool,
            auto_reload=auto_reload,
            source=source,
            observed=observed,
        )

    def meter_gate(self, provider: str, pool: str) -> dict:
        return meter.meter_gate(self.store, provider=provider, pool=pool)
