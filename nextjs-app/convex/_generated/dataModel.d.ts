/* eslint-disable */
/**
 * Generated data model types.
 *
 * THIS CODE IS AUTOMATICALLY GENERATED.
 *
 * To regenerate, run `npx convex dev`.
 * @module
 */

import { AnyDataModel } from "convex/server";
import type { GenericId } from "convex/values";

/**
 * No-op type for Convex code generation.
 *
 * Used to ensure type safety for table names and document IDs.
 */
export type DataModel = AnyDataModel;

/**
 * Utility type for document IDs.
 */
export type Id<TableName extends keyof DataModel["tables"]> = GenericId<TableName>;

/**
 * Utility type for documents.
 */
export type Doc<TableName extends keyof DataModel["tables"]> = DataModel["tables"][TableName]["document"];