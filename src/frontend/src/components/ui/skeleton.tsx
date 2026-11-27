import { type HTMLAttributes, memo } from "react";
import { cn } from "../../utils/utils";

const Skeleton = memo(function Skeleton({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-border", className)}
      {...props}
    />
  );
});

export { Skeleton };
