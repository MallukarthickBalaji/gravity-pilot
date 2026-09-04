import type { QueryKey, UseMutationOptions, UseMutationResult, UseQueryOptions, UseQueryResult } from '@tanstack/react-query';
import type { BackendStatus, ChatMessage, ChatSession, ChatSessionInput, HealthStatus } from './api.schemas';
import { customFetch } from '../custom-fetch';
import type { ErrorType, BodyType } from '../custom-fetch';
type AwaitedInput<T> = PromiseLike<T> | T;
type Awaited<O> = O extends AwaitedInput<infer T> ? T : never;
type SecondParameter<T extends (...args: never) => unknown> = Parameters<T>[1];
export declare const getHealthCheckUrl: () => string;
/**
 * @summary Health check
 */
export declare const healthCheck: (options?: Parameters<typeof customFetch>[1]) => Promise<HealthStatus>;
export declare const getHealthCheckQueryKey: () => readonly ["/api/healthz"];
export declare const getHealthCheckQueryOptions: <TData = Awaited<ReturnType<typeof healthCheck>>, TError = ErrorType<unknown>>(options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof healthCheck>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}) => UseQueryOptions<Awaited<ReturnType<typeof healthCheck>>, TError, TData> & {
    queryKey: QueryKey;
};
export type HealthCheckQueryResult = NonNullable<Awaited<ReturnType<typeof healthCheck>>>;
export type HealthCheckQueryError = ErrorType<unknown>;
/**
 * @summary Health check
 */
export declare function useHealthCheck<TData = Awaited<ReturnType<typeof healthCheck>>, TError = ErrorType<unknown>>(options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof healthCheck>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}): UseQueryResult<TData, TError> & {
    queryKey: QueryKey;
};
export declare const getGetChatStatusUrl: () => string;
/**
 * @summary Get backend mode and capabilities
 */
export declare const getChatStatus: (options?: Parameters<typeof customFetch>[1]) => Promise<BackendStatus>;
export declare const getGetChatStatusQueryKey: () => readonly ["/api/chat/status"];
export declare const getGetChatStatusQueryOptions: <TData = Awaited<ReturnType<typeof getChatStatus>>, TError = ErrorType<unknown>>(options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof getChatStatus>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}) => UseQueryOptions<Awaited<ReturnType<typeof getChatStatus>>, TError, TData> & {
    queryKey: QueryKey;
};
export type GetChatStatusQueryResult = NonNullable<Awaited<ReturnType<typeof getChatStatus>>>;
export type GetChatStatusQueryError = ErrorType<unknown>;
/**
 * @summary Get backend mode and capabilities
 */
export declare function useGetChatStatus<TData = Awaited<ReturnType<typeof getChatStatus>>, TError = ErrorType<unknown>>(options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof getChatStatus>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}): UseQueryResult<TData, TError> & {
    queryKey: QueryKey;
};
export declare const getListChatSessionsUrl: () => string;
/**
 * @summary List recent chat sessions
 */
export declare const listChatSessions: (options?: Parameters<typeof customFetch>[1]) => Promise<ChatSession[]>;
export declare const getListChatSessionsQueryKey: () => readonly ["/api/chat/sessions"];
export declare const getListChatSessionsQueryOptions: <TData = Awaited<ReturnType<typeof listChatSessions>>, TError = ErrorType<unknown>>(options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof listChatSessions>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}) => UseQueryOptions<Awaited<ReturnType<typeof listChatSessions>>, TError, TData> & {
    queryKey: QueryKey;
};
export type ListChatSessionsQueryResult = NonNullable<Awaited<ReturnType<typeof listChatSessions>>>;
export type ListChatSessionsQueryError = ErrorType<unknown>;
/**
 * @summary List recent chat sessions
 */
export declare function useListChatSessions<TData = Awaited<ReturnType<typeof listChatSessions>>, TError = ErrorType<unknown>>(options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof listChatSessions>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}): UseQueryResult<TData, TError> & {
    queryKey: QueryKey;
};
export declare const getCreateChatSessionUrl: () => string;
/**
 * @summary Create a new chat session
 */
export declare const createChatSession: (chatSessionInput: ChatSessionInput, options?: Parameters<typeof customFetch>[1]) => Promise<ChatSession>;
export declare const getCreateChatSessionMutationOptions: <TError = ErrorType<unknown>, TContext = unknown>(options?: {
    mutation?: UseMutationOptions<Awaited<ReturnType<typeof createChatSession>>, TError, {
        data: BodyType<ChatSessionInput>;
    }, TContext>;
    request?: SecondParameter<typeof customFetch>;
}) => UseMutationOptions<Awaited<ReturnType<typeof createChatSession>>, TError, {
    data: BodyType<ChatSessionInput>;
}, TContext>;
export type CreateChatSessionMutationResult = NonNullable<Awaited<ReturnType<typeof createChatSession>>>;
export type CreateChatSessionMutationBody = BodyType<ChatSessionInput>;
export type CreateChatSessionMutationError = ErrorType<unknown>;
/**
* @summary Create a new chat session
*/
export declare const useCreateChatSession: <TError = ErrorType<unknown>, TContext = unknown>(options?: {
    mutation?: UseMutationOptions<Awaited<ReturnType<typeof createChatSession>>, TError, {
        data: BodyType<ChatSessionInput>;
    }, TContext>;
    request?: SecondParameter<typeof customFetch>;
}) => UseMutationResult<Awaited<ReturnType<typeof createChatSession>>, TError, {
    data: BodyType<ChatSessionInput>;
}, TContext>;
export declare const getGetChatSessionUrl: (sessionId: string) => string;
/**
 * @summary Get a single chat session
 */
export declare const getChatSession: (sessionId: string, options?: Parameters<typeof customFetch>[1]) => Promise<ChatSession>;
export declare const getGetChatSessionQueryKey: (sessionId: string) => readonly [`/api/chat/sessions/${string}`];
export declare const getGetChatSessionQueryOptions: <TData = Awaited<ReturnType<typeof getChatSession>>, TError = ErrorType<void>>(sessionId: string, options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof getChatSession>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}) => UseQueryOptions<Awaited<ReturnType<typeof getChatSession>>, TError, TData> & {
    queryKey: QueryKey;
};
export type GetChatSessionQueryResult = NonNullable<Awaited<ReturnType<typeof getChatSession>>>;
export type GetChatSessionQueryError = ErrorType<void>;
/**
 * @summary Get a single chat session
 */
export declare function useGetChatSession<TData = Awaited<ReturnType<typeof getChatSession>>, TError = ErrorType<void>>(sessionId: string, options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof getChatSession>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}): UseQueryResult<TData, TError> & {
    queryKey: QueryKey;
};
export declare const getDeleteChatSessionUrl: (sessionId: string) => string;
/**
 * @summary Delete a single chat session
 */
export declare const deleteChatSession: (sessionId: string, options?: Parameters<typeof customFetch>[1]) => Promise<void>;
export declare const getDeleteChatSessionMutationOptions: <TError = ErrorType<void>, TContext = unknown>(options?: {
    mutation?: UseMutationOptions<Awaited<ReturnType<typeof deleteChatSession>>, TError, {
        sessionId: string;
    }, TContext>;
    request?: SecondParameter<typeof customFetch>;
}) => UseMutationOptions<Awaited<ReturnType<typeof deleteChatSession>>, TError, {
    sessionId: string;
}, TContext>;
export type DeleteChatSessionMutationResult = NonNullable<Awaited<ReturnType<typeof deleteChatSession>>>;
export type DeleteChatSessionMutationError = ErrorType<void>;
/**
* @summary Delete a single chat session
*/
export declare const useDeleteChatSession: <TError = ErrorType<void>, TContext = unknown>(options?: {
    mutation?: UseMutationOptions<Awaited<ReturnType<typeof deleteChatSession>>, TError, {
        sessionId: string;
    }, TContext>;
    request?: SecondParameter<typeof customFetch>;
}) => UseMutationResult<Awaited<ReturnType<typeof deleteChatSession>>, TError, {
    sessionId: string;
}, TContext>;
export declare const getGetSessionMessagesUrl: (sessionId: string) => string;
/**
 * @summary Get all messages for a session
 */
export declare const getSessionMessages: (sessionId: string, options?: Parameters<typeof customFetch>[1]) => Promise<ChatMessage[]>;
export declare const getGetSessionMessagesQueryKey: (sessionId: string) => readonly [`/api/chat/sessions/${string}/messages`];
export declare const getGetSessionMessagesQueryOptions: <TData = Awaited<ReturnType<typeof getSessionMessages>>, TError = ErrorType<unknown>>(sessionId: string, options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof getSessionMessages>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}) => UseQueryOptions<Awaited<ReturnType<typeof getSessionMessages>>, TError, TData> & {
    queryKey: QueryKey;
};
export type GetSessionMessagesQueryResult = NonNullable<Awaited<ReturnType<typeof getSessionMessages>>>;
export type GetSessionMessagesQueryError = ErrorType<unknown>;
/**
 * @summary Get all messages for a session
 */
export declare function useGetSessionMessages<TData = Awaited<ReturnType<typeof getSessionMessages>>, TError = ErrorType<unknown>>(sessionId: string, options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof getSessionMessages>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}): UseQueryResult<TData, TError> & {
    queryKey: QueryKey;
};
export {};
//# sourceMappingURL=api.d.ts.map