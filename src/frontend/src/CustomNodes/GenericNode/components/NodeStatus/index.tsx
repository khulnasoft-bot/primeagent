import cn from "classnames"; // Assuming you have classnames installed
import React, { useEffect, useRef, useState } from "react";
import { useHotkeys } from "react-hotkeys-hook";
import { getSpecificClassFromBuildStatus } from "@/CustomNodes/helpers/get-class-from-build-status";
import { mutateTemplate } from "@/CustomNodes/helpers/mutate-template";
import useIconStatus from "@/CustomNodes/hooks/use-icons-status";
import useUpdateValidationStatus from "@/CustomNodes/hooks/use-update-validation-status";
import useValidationStatusString from "@/CustomNodes/hooks/use-validation-status-string";
import ShadTooltip from "@/components/common/shadTooltipComponent";
import { Button } from "@/components/ui/button";
import { ICON_STROKE_WIDTH } from "@/constants/constants";
import type { EventDeliveryType } from "@/constants/enums";
import { BuildStatus } from "@/constants/enums";
import { usePostTemplateValue } from "@/controllers/API/queries/nodes/use-post-template-value";
import { track } from "@/customization/utils/analytics";
import { customOpenNewTab } from "@/customization/utils/custom-open-new-tab";
import useAlertStore from "@/stores/alertStore";
import { useDarkStore } from "@/stores/darkStore";
import useFlowStore from "@/stores/flowStore";
import { useShortcutsStore } from "@/stores/shortcuts";
import { useUtilityStore } from "@/stores/utilityStore";
import type {
  APIClassType,
  InputFieldType,
  VertexBuildTypeAPI,
} from "@/types/api";
import type { AllNodeType, NodeDataType } from "@/types/flow";

interface NodeStatusProps {
  nodeId: string;
  data: NodeDataType;
  nodeAuth?: { name?: string; auth_tooltip?: string };
  showNodeStatus?: boolean;
  showNode?: boolean;
  display_name: string;
  version?: string;
  conditionSuccess?: boolean;
  validationStatus: VertexBuildTypeAPI | null;
  buildStatus?: BuildStatus;
  isBuilding?: boolean;
  isAuthenticated: boolean;
  connectionLink: string;
  apiKeyValue?: string;
  eventDeliveryConfig?: EventDeliveryType;
  isOutdated?: boolean;
  isUserEdited?: boolean;
  dismissAll?: boolean;
  isBreakingChange?: boolean;
  frozen?: boolean;
  lastRunTime?: string | null;
  selected?: boolean;
  setNode: (
    nodeId: string,
    updater: AllNodeType | ((old: AllNodeType) => AllNodeType),
    flag?: boolean,
  ) => void;
  normalizeTimeString: (duration: number) => string;
  buildFlow: (opts: {
    stopNodeId: string;
    eventDelivery?: EventDeliveryType;
  }) => void;
  getValidationStatus: () => void;
  IconComponent: React.ElementType;
  pollingIntervalMs?: number;
  pollingTimeoutMs?: number;
}

const POLLING_INTERVAL = 3000;
const POLLING_TIMEOUT = 60000;

export default function NodeStatus({
  nodeId,
  data,
  nodeAuth,
  showNodeStatus = false,
  showNode = true,
  display_name,
  version,
  conditionSuccess = false,
  validationStatus,
  buildStatus,
  isBuilding = false,
  isAuthenticated,
  connectionLink,
  apiKeyValue,
  eventDeliveryConfig,
  isOutdated = false,
  isUserEdited = false,
  dismissAll = false,
  isBreakingChange = false,
  frozen = false,
  lastRunTime = null,
  selected = false,
  setNode,
  normalizeTimeString,
  buildFlow,
  getValidationStatus,
  IconComponent,
  pollingIntervalMs = POLLING_INTERVAL,
  pollingTimeoutMs = POLLING_TIMEOUT,
}: NodeStatusProps) {
  const pollingInterval = useRef<NodeJS.Timeout | null>(null);
  const pollingTimeout = useRef<NodeJS.Timeout | null>(null);

  const [isPolling, setIsPolling] = useState(false);
  const [validationString, setValidationString] = useState("");
  const [validationStatusLocal, setValidationStatus] =
    useState<VertexBuildTypeAPI | null>(validationStatus);
  const [isHovered, setIsHovered] = useState(false);
  const [_borderColor, setBorderColor] = useState<string>("");

  const postTemplateValue = usePostTemplateValue();

  // Start polling function
  const startPolling = () => {
    setIsPolling(true);
    mutateTemplate(
      () => {
        const updatedAuth = Object.values(data?.node?.template ?? {}).find(
          (value: InputFieldType) => value?.type === "auth",
        );
        const oauthUrl = updatedAuth?.value;

        if (
          oauthUrl &&
          typeof oauthUrl === "string" &&
          oauthUrl.startsWith("http")
        ) {
          customOpenNewTab(oauthUrl);
        }
      },
      postTemplateValue,
      setErrorData,
      nodeAuth?.name ?? "auth_link",
      () => {
        pollingInterval.current = setInterval(() => {
          mutateTemplate(
            { validate: data.node?.template?.auth?.value || "" },
            data.id,
            data.node,
            (newNode: APIClassType) => {
              setNode(nodeId, (old: AllNodeType) => ({
                ...old,
                data: { ...old.data, node: newNode } as NodeDataType,
              }));
            },
            postTemplateValue,
            setErrorData,
            nodeAuth?.name ?? "auth_link",
            () => {},
            data.node.tool_mode,
          );
        }, pollingIntervalMs);

        pollingTimeout.current = setTimeout(() => {
          stopPolling();
        }, pollingTimeoutMs);
      },
      data.node.tool_mode,
    );
  };

  // Stop polling function
  const stopPolling = () => {
    setIsPolling(false);
    if (pollingInterval.current) clearInterval(pollingInterval.current);
    if (pollingTimeout.current) clearTimeout(pollingTimeout.current);
  };

  useEffect(() => {
    if (isAuthenticated) {
      stopPolling();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]);

  // Disconnect handler
  const handleDisconnect = () => {
    setIsPolling(true);
    mutateTemplate(
      "disconnect",
      data.id,
      data.node,
      (newNode: APIClassType) => {
        setNode(nodeId, (old: AllNodeType) => ({
          ...old,
          data: { ...old.data, node: newNode } as NodeDataType,
        }));
      },
      postTemplateValue,
      setErrorData,
      nodeAuth?.name ?? "auth_link",
      () => {
        setIsPolling(false);
      },
      data.node.tool_mode,
    );
  };

  // Handler for running build with keyboard shortcut
  const handlePlayWShortcut = () => {
    if (buildStatus === BuildStatus.BUILDING || isBuilding || !selected) return;
    setValidationStatus(null);
    buildFlow({
      stopNodeId: nodeId,
      eventDelivery: eventDeliveryConfig,
    });
  };

  const playShortcut = useShortcutsStore((state) => state.play);
  const flowPool = useFlowStore((state) => state.flowPool);

  useHotkeys(playShortcut, handlePlayWShortcut, { preventDefault: true });
  useValidationStatusString(validationStatusLocal, setValidationString);
  useUpdateValidationStatus(
    nodeId,
    flowPool,
    setValidationStatus,
    getValidationStatus,
  );

  // Helper functions for CSS classes
  const getBaseBorderClass = (selectedFlag: boolean) => {
    const className =
      selectedFlag && !isBuilding
        ? " border ring-[0.75px] ring-muted-foreground border-muted-foreground hover:shadow-node"
        : "border ring-[0.5px] hover:shadow-node ring-border";
    const frozenClass = selectedFlag ? "border-ring-frozen" : "border-frozen";
    const updateClass =
      isOutdated && !isUserEdited && !dismissAll && isBreakingChange
        ? "border-warning"
        : "";
    return cn(frozen ? frozenClass : className, updateClass);
  };

  const getNodeBorderClassName = (
    selectedFlag: boolean | undefined,
    buildStatusFlag: BuildStatus | undefined,
    validationStatusFlag: VertexBuildTypeAPI | null,
  ) => {
    const specificClassFromBuildStatus = getSpecificClassFromBuildStatus(
      buildStatusFlag,
      validationStatusFlag,
      isBuilding,
    );
    const baseBorderClass = getBaseBorderClass(selectedFlag ?? false);
    return cn(baseBorderClass, specificClassFromBuildStatus);
  };

  useEffect(() => {
    setBorderColor(
      getNodeBorderClassName(selected, buildStatus, validationStatusLocal),
    );
  }, [
    selected,
    showNode,
    buildStatus,
    validationStatusLocal,
    isOutdated,
    isUserEdited,
    frozen,
    dismissAll,
  ]);

  // Update node version after build completes
  useEffect(() => {
    if (buildStatus === BuildStatus.BUILT && !isBuilding) {
      setNode(
        nodeId,
        (old: AllNodeType) => ({
          ...old,
          data: {
            ...old.data,
            node: {
              ...(old.data as NodeDataType).node,
              lf_version: version,
            },
          } as NodeDataType,
        }),
        false,
      );
    }
  }, [buildStatus, isBuilding, nodeId, setNode, version]);

  const stopBuilding = useFlowStore((state) => state.stopBuilding);
  const setFlowPool = useFlowStore((state) => state.setFlowPool);

  // Run build button handler
  const handleClickRun = () => {
    setFlowPool({});

    if (buildStatus === BuildStatus.BUILDING && isHovered) {
      stopBuilding();
      return;
    }
    if (buildStatus === BuildStatus.BUILDING || isBuilding) return;

    buildFlow({
      stopNodeId: nodeId,
      eventDelivery: eventDeliveryConfig,
    });
    track("Flow Build - Clicked", { stopNodeId: nodeId });
  };

  // Icon name logic for run button
  const iconName =
    buildStatus === BuildStatus.BUILDING
      ? isHovered
        ? "Square"
        : "Loader2"
      : "Play";

  // CSS classes for icon
  const iconClasses = cn(
    "h-3.5 w-3.5 transition-all group-hover/node:opacity-100",
    isHovered ? "text-foreground" : "text-muted-foreground",
    buildStatus === BuildStatus.BUILDING &&
      (isHovered ? "text-status-red" : "animate-spin"),
  );

  // Tooltip content for run button
  const getTooltipContent = () => {
    if (buildStatus === BuildStatus.BUILDING && isHovered) {
      return "Stop build";
    }
    return "Run component";
  };

  // Connect button click handler
  const handleClickConnect = () => {
    if (connectionLink === "error") return;
    if (isAuthenticated) {
      handleDisconnect();
    } else {
      startPolling();
    }
  };

  // Connection button CSS classes
  const getConnectionButtonClasses = (
    connectionLinkFlag: string,
    isAuthenticatedFlag: boolean,
    isPollingFlag: boolean,
  ): string => {
    return cn(
      "nodrag button-run-bg group relative h-4 w-4 p-0.5 rounded-sm border border-accent-amber-foreground transition-colors hover:bg-accent-amber",
      connectionLinkFlag === "error"
        ? "border-destructive text-destructive"
        : isAuthenticatedFlag && !isPollingFlag
          ? "border-accent-emerald-foreground hover:border-accent-amber-foreground"
          : "",
      connectionLinkFlag === "" &&
        (!apiKeyValue || apiKeyValue === "COMPOSIO_API_KEY") &&
        "cursor-not-allowed opacity-50",
    );
  };

  // Connection icon CSS classes
  const getConnectionIconClasses = (
    connectionLinkFlag: string,
    isAuthenticatedFlag: boolean,
    isPollingFlag: boolean,
  ): string => {
    return cn(
      "transition-opacity h-2.5 w-2.5",
      connectionLinkFlag === "error"
        ? "text-destructive"
        : isAuthenticatedFlag && !isPollingFlag
          ? "text-accent-emerald-foreground"
          : "text-accent-amber-foreground",
      isPollingFlag && "animate-spin",
      isAuthenticatedFlag && !isPollingFlag ? "group-hover:opacity-0" : "",
    );
  };

  // Test ID for connection button
  const getDataTestId = () => {
    if (isAuthenticated && !isPolling) {
      return `button_connected_${display_name.toLowerCase()}`;
    }
    if (connectionLink === "error") {
      return `button_error_${display_name.toLowerCase()}`;
    }
    return `button_disconnected_${display_name.toLowerCase()}`;
  };

  const iconStatus = useIconStatus(buildStatus, validationStatusLocal);

  return (
    <div className="flex shrink-0 items-center gap-2">
      {(showNodeStatus || nodeAuth) && (
        <div className="flex items-center gap-2 self-center">
          {showNodeStatus && (
            <ShadTooltip
              styleClasses={cn(
                "border rounded-xl",
                conditionSuccess
                  ? "border-accent-emerald-foreground bg-success-background"
                  : "border-destructive bg-error-background",
              )}
              content={
                <BuildStatusDisplay
                  buildStatus={buildStatus}
                  validationStatus={validationStatusLocal}
                  validationString={validationString}
                  lastRunTime={lastRunTime}
                />
              }
              side="bottom"
            >
              <div className="cursor-help">
                {conditionSuccess && validationStatusLocal?.data?.duration ? (
                  <div
                    className="flex rounded-sm px-1 font-mono text-xs text-accent-emerald-foreground transition-colors hover:bg-accent-emerald"
                    data-testid={`node_duration_${display_name.toLowerCase()}`}
                  >
                    <span>
                      {normalizeTimeString(validationStatusLocal.data.duration)}
                    </span>
                  </div>
                ) : (
                  <div
                    data-testid={`node_status_icon_${display_name.toLowerCase()}_${buildStatus?.toLowerCase()}`}
                    className="flex items-center self-center"
                  >
                    {iconStatus}
                  </div>
                )}
              </div>
            </ShadTooltip>
          )}

          {nodeAuth && showNode && (
            <ShadTooltip content={nodeAuth.auth_tooltip || "Connect"}>
              <div>
                <Button
                  unstyled
                  disabled={
                    (connectionLink === "" &&
                      (!apiKeyValue || apiKeyValue === "COMPOSIO_API_KEY")) ||
                    connectionLink === "error"
                  }
                  className={getConnectionButtonClasses(
                    connectionLink,
                    isAuthenticated,
                    isPolling,
                  )}
                  onClick={handleClickConnect}
                  data-testid={getDataTestId()}
                >
                  <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
                    <IconComponent
                      name={
                        isPolling
                          ? "Loader2"
                          : isAuthenticated
                            ? "Link"
                            : "AlertTriangle"
                      }
                      className={getConnectionIconClasses(
                        connectionLink,
                        isAuthenticated,
                        isPolling,
                      )}
                      strokeWidth={ICON_STROKE_WIDTH}
                    />
                  </div>
                  <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
                    <IconComponent
                      name={"Unlink"}
                      className={cn(
                        "h-2.5 w-2.5 text-accent-amber-foreground opacity-0 transition-opacity",
                        isAuthenticated && !isPolling
                          ? "group-hover:opacity-100"
                          : "",
                      )}
                      strokeWidth={ICON_STROKE_WIDTH}
                    />
                  </div>
                </Button>
              </div>
            </ShadTooltip>
          )}
        </div>
      )}
      {showNode && (
        <ShadTooltip content={getTooltipContent()}>
          <div
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            onClick={handleClickRun}
            className="-m-0.5"
            role="button"
            tabIndex={0}
          >
            <Button unstyled className="nodrag button-run-bg group">
              <div data-testid={`button_run_${display_name.toLowerCase()}`}>
                <IconComponent
                  name={iconName}
                  className={iconClasses}
                  strokeWidth={ICON_STROKE_WIDTH}
                />
              </div>
            </Button>
          </div>
        </ShadTooltip>
      )}
    </div>
  );
}
