import { writable } from "svelte/store";

export const isAuthenticated = writable(false);
export const username = writable("");
export const activeTab = writable("checks");
