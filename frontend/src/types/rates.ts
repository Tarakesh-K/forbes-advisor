export type Rate = {
  provider: string;
  rate_type: string;
  rate_value: number;
  effective_date: Date;
  ingestion_ts: string;
};

export interface RateComponentProps {
  initialRates: Rate[];
}

export type RateTableProps = {
  data: Rate[];
  loading: boolean;
};

export type DateRange = {
  fromDate: string;
  toDate: string;
};

export type RateHistory = {
  provider: string;
  type: string;
  range: string;
  from_date: string;
  to_date: string;
}
