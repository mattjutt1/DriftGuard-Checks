/* eslint-disable */
/**
 * Generated `api` utility.
 *
 * THIS CODE IS AUTOMATICALLY GENERATED.
 *
 * To regenerate, run `npx convex dev`.
 * @module
 */

import type {
  ApiFromModules,
  FilterApi,
  FunctionReference,
} from "convex/server";
import type * as actions from "../actions.js";
import type * as hfIntegration from "../hfIntegration.js";
import type * as hfOptimize from "../hfOptimize.js";
import type * as hfspace from "../hfspace.js";
import type * as http from "../http.js";
import type * as ollama from "../ollama.js";
import type * as optimizations from "../optimizations.js";
import type * as seedData from "../seedData.js";
import type * as sessions from "../sessions.js";
import type * as testLogs from "../testLogs.js";

/**
 * A utility for referencing Convex functions in your app's API.
 *
 * Usage:
 * ```js
 * const myFunctionReference = api.myModule.myFunction;
 * ```
 */
declare const fullApi: ApiFromModules<{
  actions: typeof actions;
  hfIntegration: typeof hfIntegration;
  hfOptimize: typeof hfOptimize;
  hfspace: typeof hfspace;
  http: typeof http;
  ollama: typeof ollama;
  optimizations: typeof optimizations;
  seedData: typeof seedData;
  sessions: typeof sessions;
  testLogs: typeof testLogs;
}>;
export declare const api: FilterApi<
  typeof fullApi,
  FunctionReference<any, "public">
>;
export declare const internal: FilterApi<
  typeof fullApi,
  FunctionReference<any, "internal">
>;
