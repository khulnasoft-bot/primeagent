from typing import Final

DEFAULT_SEGMENT_WRITE_KEY: Final = ""

IBM_PRODUCT_PROPERTIES: Final = {
    "UT30": "30AS5",
    "productCode": "WW3151",
    "productCodeType": "WWPC",
    "productPlanName": "opensource",
    "productPlanType": "freemium",
    "productTitle": "PrimeAgent",
}

IBM_COMMON_EVENT_MAP: Final[dict[str, tuple[str, str | None]]] = {
    "version": ("Started Process", "PrimeAgent"),
    "run": ("Ran Process", "PrimeAgent Flow"),
    "deployment": ("Ran Process", "PrimeAgent Deployment"),
    "integration_action": ("Ran Process", "PrimeAgent Integration"),
    "deployment_provider": ("Ran Process", "PrimeAgent Deployment Provider"),
    "deployment_run": ("Ran Process", "PrimeAgent Deployment"),
    "shutdown": ("Ended Process", "PrimeAgent"),
    "email": ("UI Interaction", None),
    "playground": ("Ran Process", "PrimeAgent Playground"),
    "component": ("Ran Process", "PrimeAgent Component"),
    "component_inputs": ("Ran Process", "PrimeAgent Component Input"),
    "component_index": ("Ran Process", "PrimeAgent Component Index"),
    "exception": ("Ended Process", "PrimeAgent Exception"),
    "mcp_tool": ("Ran Process", "PrimeAgent MCP Tool"),
}


def get_ibm_common_event(path: str | None) -> tuple[str, str | None, str]:
    legacy_event = path or "version"
    event, process_type = IBM_COMMON_EVENT_MAP.get(
        legacy_event,
        ("Ran Process", f"PrimeAgent {legacy_event.replace('_', ' ').title()}"),
    )
    return event, process_type, legacy_event
