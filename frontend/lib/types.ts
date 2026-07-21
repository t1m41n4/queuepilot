export type Bank = { id: number; name: string };
export type Branch = { id: number; name: string };

export type QueueJoinResponse = {
  queue_entry_id: number;
  queue_number: string;
  status: string;
  estimated_wait: number;
};

export type QueueStatusResponse = {
  queue_number: string;
  branch_name: string;
  status: string;
  position: number;
  estimated_wait: number;
};

export type StaffQueueItem = {
  queue_number?: string;
  customer_name?: string;
  status?: string;
  estimated_wait?: number;
  action?: string;
};

export type StaffDashboardResponse = {
  queue_status?: string;
  waiting?: number;
  ready?: number;
  checked_in?: number;
  current_customer?: string | null;
  queue?: StaffQueueItem[];
};

export type AssistantResponse = { answer: string };
