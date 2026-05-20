import { Component, onMounted, onWillUnmount, useRef, useState } from "@odoo/owl";

import { Dropdown } from "@web/core/dropdown/dropdown";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { debounce } from "@web/core/utils/timing";

const RECENT_STORAGE_KEY = "bb_global_search.recent_records";
const RECENT_LIMIT = 15;

export class GlobalSearch extends Component {
    static components = { Dropdown };
    static props = [];
    static template = "global_search.GlobalSearchMenu";

    setup() {
        this.inputRef = useRef("searchInput");
        this.buttonRef = useRef("searchButton");
        this.state = useState({
            query: "",
            groups: [],
            flatResults: [],
            selectedIndex: 0,
            showingRecent: false,
            searched: false,
        });
        this.orm = useService("orm");
        this.action = useService("action");
        this.models = [];
        this.limitPerGroup = 10;
        this.limitTotal = 40;
        this.onSearchInputDebounced = debounce((value) => this.performSearch(value), 300);
        this._globalKeydown = (ev) => this.onGlobalKeydown(ev);

        onMounted(() => window.addEventListener("keydown", this._globalKeydown));
        onWillUnmount(() => window.removeEventListener("keydown", this._globalKeydown));
    }

    async getSelectedModels() {
        if (this.models.length) {
            return;
        }
        const response = await rpc("/company/get_search_models");
        if (Array.isArray(response)) {
            // Backward compatibility with the original controller payload.
            this.models = response;
            return;
        }
        this.models = response.models || [];
        this.limitPerGroup = Number(response.limit_per_group || 0);
        this.limitTotal = Number(response.limit_total || 0);
    }

    async getRecords(value) {
        const result = [];
        let idCnt = 1;
        const query = (value || "").trim();

        if (!query || query.length < 2) {
            return result;
        }

        const fetchLimit = this.limitPerGroup > 0 ? this.limitPerGroup * 3 : 0;
        for (let i = 0; i < this.models.length; i++) {
            const model = this.models[i].model;
            const modelLabel = this.models[i].name;
            try {
                const records = await this.orm.call(model, "bb_global_search", [], {
                    name: query,
                    operator: "ilike",
                    limit: fetchLimit,
                });

                for (let j = 0; j < records.length; j++) {
                    const record = records[j];
                    const label = record[3] || modelLabel;
                    result.push({
                        id: idCnt,
                        name: record[1],
                        match_info: record[2] || "",
                        label: label,
                        group: record[4] || label || modelLabel,
                        priority: Number(record[5] || 500),
                        rec_id: record[0],
                        model: model,
                        resModel: modelLabel,
                        recent: false,
                    });
                    idCnt++;
                }
            } catch (error) {
                console.warn(`Global search skipped ${model}:`, error);
            }
        }
        return result;
    }

    async performSearch(value) {
        const query = (value || "").trim();
        this.state.query = query;
        if (query.length < 2) {
            this.showRecent();
            return;
        }
        await this.getSelectedModels();
        const records = await this.getRecords(query);
        this.setResults(records, false, true);
    }

    setResults(records, showingRecent = false, searched = false) {
        const limited = this.applyLimits(records || []);
        const groups = this.buildGroups(limited);
        this.state.flatResults = limited;
        this.state.groups = groups;
        this.state.selectedIndex = limited.length ? 0 : -1;
        this.state.showingRecent = showingRecent;
        this.state.searched = searched;
    }

    applyLimits(records) {
        const sorted = [...records].sort((a, b) => {
            if (a.priority !== b.priority) {
                return a.priority - b.priority;
            }
            return (a.name || "").localeCompare(b.name || "");
        });

        const perGroupCounts = {};
        const output = [];
        for (const record of sorted) {
            const group = record.group || "Other";
            perGroupCounts[group] = perGroupCounts[group] || 0;
            if (this.limitPerGroup > 0 && perGroupCounts[group] >= this.limitPerGroup) {
                continue;
            }
            if (this.limitTotal > 0 && output.length >= this.limitTotal) {
                break;
            }
            perGroupCounts[group]++;
            record.global_index = output.length;
            output.push(record);
        }
        return output;
    }

    buildGroups(records) {
        const groupsByName = new Map();
        for (const record of records) {
            const groupName = record.group || "Other";
            if (!groupsByName.has(groupName)) {
                groupsByName.set(groupName, { name: groupName, items: [] });
            }
            groupsByName.get(groupName).items.push(record);
        }
        return Array.from(groupsByName.values());
    }

    onSearchInput(ev) {
        const value = ev?.target?.value || "";
        this.state.query = value;
        if (value.trim().length < 2) {
            this.showRecent();
            return;
        }
        this.onSearchInputDebounced(value);
    }

    onSearchInputKeydown(ev) {
        if (ev.key === "ArrowDown") {
            ev.preventDefault();
            this.moveSelection(1);
        } else if (ev.key === "ArrowUp") {
            ev.preventDefault();
            this.moveSelection(-1);
        } else if (ev.key === "Enter") {
            ev.preventDefault();
            this.openSelected({ newTab: ev.ctrlKey || ev.metaKey });
        } else if (ev.key === "Escape") {
            ev.preventDefault();
            this.closeDropdown();
        }
    }

    onGlobalKeydown(ev) {
        if ((ev.ctrlKey || ev.metaKey) && ev.shiftKey && ev.key.toLowerCase() === "f") {
            ev.preventDefault();
            this.openAndFocus();
        }
    }

    onSearchButtonClick() {
        window.setTimeout(() => {
            this.focusInput();
            if (!this.state.query) {
                this.showRecent();
            }
        }, 0);
    }

    openAndFocus() {
        if (!this.inputRef.el) {
            this.buttonRef.el?.click();
        }
        window.setTimeout(() => {
            this.focusInput();
            if (!this.state.query) {
                this.showRecent();
            }
        }, 0);
    }

    focusInput() {
        this.inputRef.el?.focus();
        this.inputRef.el?.select();
    }

    closeDropdown() {
        this.buttonRef.el?.click();
    }

    moveSelection(delta) {
        if (!this.state.flatResults.length) {
            return;
        }
        const max = this.state.flatResults.length - 1;
        let next = this.state.selectedIndex + delta;
        if (next < 0) {
            next = max;
        } else if (next > max) {
            next = 0;
        }
        this.state.selectedIndex = next;
    }

    openSelected({ newTab = false } = {}) {
        const record = this.state.flatResults[this.state.selectedIndex];
        if (record) {
            this.openRecord(record, { newTab });
        }
    }

    onResultClick(record, ev) {
        this.openRecord(record, { newTab: ev.ctrlKey || ev.metaKey });
    }

    onResultAuxClick(record, ev) {
        if (ev.button === 1) {
            ev.preventDefault();
            this.openRecord(record, { newTab: true });
        }
    }

    async openRecord(record, { newTab = false } = {}) {
        this.addRecent(record);
        if (newTab) {
            window.open(this.recordUrl(record), "_blank", "noopener");
            return;
        }
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: record.model,
            views: [[false, "form"]],
            res_id: parseInt(record.rec_id),
        });
        this.closeDropdown();
    }

    recordUrl(record) {
        return `/web#id=${record.rec_id}&model=${encodeURIComponent(record.model)}&view_type=form`;
    }

    showRecent() {
        const recent = this.loadRecent();
        this.setResults(recent, true, false);
    }

    loadRecent() {
        try {
            const records = JSON.parse(window.localStorage.getItem(RECENT_STORAGE_KEY) || "[]");
            return records.map((record, index) => ({
                ...record,
                id: `recent-${index}`,
                global_index: index,
                priority: index,
                group: "Recent",
                recent: true,
                match_info: "",
            }));
        } catch (_error) {
            return [];
        }
    }

    addRecent(record) {
        const recentRecord = {
            name: record.name,
            label: record.label,
            group: "Recent",
            rec_id: record.rec_id,
            model: record.model,
            resModel: record.resModel,
        };
        let existing = [];
        try {
            existing = JSON.parse(window.localStorage.getItem(RECENT_STORAGE_KEY) || "[]");
        } catch (_error) {
            existing = [];
        }
        existing = existing.filter(
            (item) => !(item.model === recentRecord.model && item.rec_id === recentRecord.rec_id)
        );
        const next = [recentRecord, ...existing].slice(0, RECENT_LIMIT);
        try {
            window.localStorage.setItem(RECENT_STORAGE_KEY, JSON.stringify(next));
        } catch (_error) {
            // Ignore localStorage failures.
        }
    }
}

registry
    .category("systray")
    .add("bb_global_search.global_search", { Component: GlobalSearch }, { sequence: 1 });
