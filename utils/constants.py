BARCODE_STATUS_COLORS = {
    "ACTIVE": "#1f77b4",  # blue
    "FAULTY": "#ff7f0e",  # orange
    "DAMAGE": "#d62728",  # red
    "IN_TRANSIT": "#2ca02c",  # green
    "IN_REQUISITION": "#9467bd",  # purple
    "IN_TRANSFER": "#8c564b",  # brown
    "RE_STOCK": "#e377c2",  # pink
    "SOLD": "#7f7f7f",  # gray
    "DISCONTINUE": "#bcbd22",  # olive
    "RETURN": "#17becf",  # teal
    "REPLACEMENT": "#aec7e8",  # light blue
    "BAD_LOSS": "#ffbb78",  # light orange
    "CAN_BE_RESOLD": "#98df8a",  # light green
    "NOT_SALABLE": "#c49c94",  # light brown
    "GSHEBA_FAULTY": "#f7b6d2",  # light pink
    "COMPANY_WARRANTY_FAULTY": "#c7c7c7",  # light gray
    "PACKET_DAMAGE": "#dbdb8d",  # light olive
    "DEFECTIVE_ON_ARRIVAL": "#9edae5",  # light teal
    "REPLACEMENT_WARRANTY_FAULTY": "#ff9896",  # light red
    "SERVICE_WARRANTY_FAULTY": "#1f77b4",  # blue (same as ACTIVE)
    "OTHERS": "#9467bd",  # purple (same as IN_REQUISITION)
}

BARCODE_STATUS_DARK_COLORS = {
    "ACTIVE": "#0d3d74",  # dark blue
    "FAULTY": "#cc5a06",  # dark orange
    "DAMAGE": "#a3181e",  # dark red
    "IN_TRANSIT": "#186922",  # dark green
    "IN_REQUISITION": "#63318c",  # dark purple
    "IN_TRANSFER": "#5c3833",  # dark brown
    "RE_STOCK": "#a34d83",  # dark pink
    "SOLD": "#4d4d4d",  # dark gray
    "DISCONTINUE": "#848b15",  # dark olive
    "RETURN": "#127387",  # dark teal
    "REPLACEMENT": "#678aa7",  # dark light blue
    "BAD_LOSS": "#cc894b",  # dark light orange
    "CAN_BE_RESOLD": "#6b995e",  # dark light green
    "NOT_SALABLE": "#8c6e62",  # dark light brown
    "GSHEBA_FAULTY": "#ad8190",  # dark light pink
    "COMPANY_WARRANTY_FAULTY": "#8c8c8c",  # dark light gray
    "PACKET_DAMAGE": "#99994b",  # dark light olive
    "DEFECTIVE_ON_ARRIVAL": "#6da2a0",  # dark light teal
    "REPLACEMENT_WARRANTY_FAULTY": "#cc6561",  # dark light red
    "SERVICE_WARRANTY_FAULTY": "#0d3d74",  # dark blue (same as ACTIVE)
    "OTHERS": "#63318c",  # dark purple (same as IN_REQUISITION)
}

ORDER_STATUS_COLORS = {
    'ORDER_RECEIVED': '#1f77b4',  # blue
    'PRODUCT_AVAILABILITY_CHECK': '#ff7f0e',  # orange
    'ORDER_CONFIRMED': '#2ca02c',  # green
    'PRODUCT_PURCHASED': '#d62728',  # red
    'PRELIMINARY_QC': '#9467bd',  # purple
    'DETAILED_QC': '#8c564b',  # brown
    'PACKAGED': '#e377c2',  # pink
    'READY_FOR_PICKUP': '#7f7f7f',  # gray
    'IN_TRANSIT': '#bcbd22',  # olive
    'DISPATCHED': '#17becf',  # teal
    'SHOP_DELIVERY_IN_TRANSIT': '#aec7e8',  # light blue
    'SHOP_RECEIVED': '#ffbb78',  # light orange
    'DELIVERED_TO_CUSTOMER': '#98df8a',  # light green
    'DELIVERED': '#07d915',  # light brown
    'CANCELLED': '#f7b6d2',  # light pink
    'RETURNED': '#c7c7c7',  # light gray
    'GSHEBA_RETURNED': '#dbdb8d',  # light olive
    'REFUNDED': '#9edae5',  # light teal
    'SHOP_TO_WAREHOUSE': '#ff9896',  # light red
    'WAREHOUSE_RECEIVED': '#1f77b4',  # blue (same as ORDER_RECEIVED)
    'WAREHOUSE_TO_SERVICE_POINT': '#ff7f0e',  # orange (same as PRODUCT_AVAILABILITY_CHECK)
    'SERVICE_POINT_RECEIVED': '#2ca02c',  # green (same as ORDER_CONFIRMED)
    'WAREHOUSE_TO_VENDOR': '#d62728',  # red (same as PRODUCT_PURCHASED)
    'IN_SERVICING': '#9467bd',  # purple (same as PRELIMINARY_QC)
    'SERVICE_POINT_TO_WAREHOUSE': '#8c564b',  # brown (same as DETAILED_QC)
    'OTHERS': '#e377c2',  # pink (same as PACKAGED)
}

ORDER_ITEM_STATUS_COLORS = {
    'ORDER_RECEIVED': '#1f77b4',  # blue
    'PRODUCT_AVAILABILITY_CHECK': '#ff7f0e',  # orange
    'ORDER_CONFIRMED': '#2ca02c',  # green
    'PRODUCT_PURCHASED': '#d62728',  # red
    'PRELIMINARY_QC': '#9467bd',  # purple
    'DETAILED_QC': '#8c564b',  # brown
    'PACKAGED': '#e377c2',  # pink
    'READY_FOR_PICKUP': '#7f7f7f',  # gray
    'IN_TRANSIT': '#bcbd22',  # olive
    'DISPATCHED': '#17becf',  # teal
    'SHOP_DELIVERY_IN_TRANSIT': '#aec7e8',  # light blue
    'SHOP_RECEIVED': '#ffbb78',  # light orange
    'DELIVERED_TO_CUSTOMER': '#98df8a',  # light green
    'DELIVERED': '#c49c94',  # light brown
    'CANCELLED': '#f7b6d2',  # light pink
    'RETURNED': '#c7c7c7',  # light gray
    'GSHEBA_RETURNED': '#dbdb8d',  # light olive
    'REFUNDED': '#9edae5',  # light teal
    'SHOP_TO_WAREHOUSE': '#ff9896',  # light red
    'WAREHOUSE_RECEIVED': '#1f77b4',  # blue (same as ORDER_RECEIVED)
    'WAREHOUSE_TO_SERVICE_POINT': '#ff7f0e',  # orange (same as PRODUCT_AVAILABILITY_CHECK)
    'SERVICE_POINT_RECEIVED': '#2ca02c',  # green (same as ORDER_CONFIRMED)
    'WAREHOUSE_TO_VENDOR': '#d62728',  # red (same as PRODUCT_PURCHASED)
    'IN_SERVICING': '#9467bd',  # purple (same as PRELIMINARY_QC)
    'SERVICE_POINT_TO_WAREHOUSE': '#8c564b',  # brown (same as DETAILED_QC)
    'OTHERS': '#e377c2',  # pink (same as PACKAGED)
}

ORDER_TYPE_COLORS = {
    "ECOMMERCE_SELL": "#1f77b4",  # blue
    "RETAIL_ECOMMERCE_SELL": "#ff7f0e",  # orange
    "POINT_OF_SELL": "#2ca02c",  # green
    "ON_THE_GO": "#d62728",  # red
    "CORPORATE_SELL": "#9467bd",  # purple
    "B2B_SELL": "#8c564b",  # brown
    "GIFT_ORDER": "#e377c2",  # pink
    "PC_BUILDER_SELL": "#7f7f7f",  # gray
    "PRE_ORDER": "#bcbd22",  # olive
    "REPLACEMENT_ORDER": "#17becf",  # teal
}
