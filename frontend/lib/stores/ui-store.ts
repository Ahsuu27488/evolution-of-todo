/** UI State Management with Zustand.

This store manages client-side UI state that doesn't come from the server:
- Modal open/close states
- Filter states
- Command Center state
- Toast notifications

Server state (tasks, user session) is managed by TanStack Query.
*/

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

// =============================================================================
// Types
// =============================================================================

export type ToastVariant = 'success' | 'error' | 'info' | 'warning';

export interface Toast {
  id: string;
  message: string;
  variant?: ToastVariant;
  duration?: number;
}

export interface FilterState {
  status: 'all' | 'pending' | 'completed';
  priority: 'all' | 'HIGH' | 'MEDIUM' | 'LOW';
  sortBy: 'created_at' | 'due_date' | 'priority' | 'title';
  sortOrder: 'asc' | 'desc';
  tag?: string;
}

export interface CommandState {
  isOpen: boolean;
  command: string;
  history: string[];
  historyIndex: number;
}

// =============================================================================
// UI Store
// =============================================================================

interface UIStore {
  // Modal states
  isTaskModalOpen: boolean;
  editingTaskId: number | null;
  isDeleteDialogOpen: boolean;
  taskToDelete: number | null;

  // Command Center state
  command: CommandState;

  // Filter state
  filters: FilterState;

  // Toast notifications
  toasts: Toast[];

  // Actions
  openTaskModal: (taskId?: number) => void;
  closeTaskModal: () => void;
  openDeleteDialog: (taskId: number) => void;
  closeDeleteDialog: () => void;

  // Command Center actions
  openCommand: () => void;
  closeCommand: () => void;
  setCommand: (command: string) => void;
  submitCommand: () => void;
  navigateHistory: (direction: 'prev' | 'next') => void;

  // Filter actions
  setFilterStatus: (status: FilterState['status']) => void;
  setFilterPriority: (priority: FilterState['priority']) => void;
  setSortBy: (sortBy: FilterState['sortBy']) => void;
  setSortOrder: (order: FilterState['sortOrder']) => void;
  setTagFilter: (tag?: string) => void;
  resetFilters: () => void;

  // Toast actions
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  clearToasts: () => void;
}

export const useUIStore = create<UIStore>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        isTaskModalOpen: false,
        editingTaskId: null,
        isDeleteDialogOpen: false,
        taskToDelete: null,

        command: {
          isOpen: false,
          command: '',
          history: [],
          historyIndex: -1,
        },

        filters: {
          status: 'all',
          priority: 'all',
          sortBy: 'created_at',
          sortOrder: 'desc',
          tag: undefined,
        },

        toasts: [],

        // Modal actions
        openTaskModal: (taskId) =>
          set({
            isTaskModalOpen: true,
            editingTaskId: taskId ?? null,
          }),

        closeTaskModal: () =>
          set({
            isTaskModalOpen: false,
            editingTaskId: null,
          }),

        openDeleteDialog: (taskId) =>
          set({
            isDeleteDialogOpen: true,
            taskToDelete: taskId,
          }),

        closeDeleteDialog: () =>
          set({
            isDeleteDialogOpen: false,
            taskToDelete: null,
          }),

        // Command Center actions
        openCommand: () =>
          set((state) => ({
            command: { ...state.command, isOpen: true },
          })),

        closeCommand: () =>
          set((state) => ({
            command: { ...state.command, isOpen: false, command: '' },
          })),

        setCommand: (command) =>
          set((state) => ({
            command: { ...state.command, command },
          })),

        submitCommand: () =>
          set((state) => {
            const { command, history } = state.command;
            if (command.trim()) {
              return {
                command: {
                  ...state.command,
                  history: [...history, command],
                  historyIndex: history.length,
                  command: '',
                },
              };
            }
            return state;
          }),

        navigateHistory: (direction) =>
          set((state) => {
            const { history, historyIndex } = state.command;
            let newIndex = historyIndex;

            if (direction === 'prev' && historyIndex > 0) {
              newIndex = historyIndex - 1;
            } else if (direction === 'next' && historyIndex < history.length - 1) {
              newIndex = historyIndex + 1;
            } else {
              return state;
            }

            return {
              command: {
                ...state.command,
                historyIndex: newIndex,
                command: history[newIndex],
              },
            };
          }),

        // Filter actions
        setFilterStatus: (status) =>
          set((state) => ({
            filters: { ...state.filters, status },
          })),

        setFilterPriority: (priority) =>
          set((state) => ({
            filters: { ...state.filters, priority },
          })),

        setSortBy: (sortBy) =>
          set((state) => ({
            filters: { ...state.filters, sortBy },
          })),

        setSortOrder: (order) =>
          set((state) => ({
            filters: { ...state.filters, sortOrder: order },
          })),

        setTagFilter: (tag) =>
          set((state) => ({
            filters: { ...state.filters, tag },
          })),

        resetFilters: () =>
          set({
            filters: {
              status: 'all',
              priority: 'all',
              sortBy: 'created_at',
              sortOrder: 'desc',
              tag: undefined,
            },
          }),

        // Toast actions
        addToast: (toast) =>
          set((state) => {
            const id = Math.random().toString(36).substring(7);
            const newToast: Toast = {
              id,
              variant: 'info',
              duration: 3000,
              ...toast,
            };

            // Auto-remove after duration
            if (newToast.duration) {
              setTimeout(() => {
                get().removeToast(id);
              }, newToast.duration);
            }

            return {
              toasts: [...state.toasts, newToast],
            };
          }),

        removeToast: (id) =>
          set((state) => ({
            toasts: state.toasts.filter((t) => t.id !== id),
          })),

        clearToasts: () => set({ toasts: [] }),
      }),
      {
        name: 'UIStore',
        // Persist only filter states, not transient UI like modals or toasts
        partialize: (state) => ({
          filters: state.filters,
        }),
      }
    ),
    { name: 'UIStore' }
  )
);

// =============================================================================
// Selectors
// =============================================================================

export const selectFilters = (state: UIStore) => state.filters;
export const selectCommand = (state: UIStore) => state.command;
