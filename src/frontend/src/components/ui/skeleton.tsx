import { cn } from "../../utils/utils";
import { memo, type HTMLAttributes } from "react";

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
