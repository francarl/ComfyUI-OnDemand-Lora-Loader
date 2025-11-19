import { app } from "/scripts/app.js";
import { api } from "/scripts/api.js";

async function onLoraChanged(lora_name) {
    try {
        const resp = await api.fetchApi("/francarl/lora_changed", {
            method: "POST",
            body: JSON.stringify({ lora_name }),
            headers: {
                "Content-Type": "application/json",
            },
        });
        if (resp.status !== 200) {
            console.error(`[OnDemandLoader] Failed to notify backend of lora change: ${resp.status}`);
        }
    } catch (e) {
        console.error("[OnDemandLoader] Failed to notify backend of lora change", e);
    }
}

app.registerExtension({
	name: "comfy.francarl.onDemandLoader",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		if (nodeData.name === "OnDemandCivitaiLikedLoraLoader") {
			const onNodeCreated = nodeType.prototype.onNodeCreated;
			nodeType.prototype.onNodeCreated = function () {
				onNodeCreated?.apply(this, arguments);

				const loraNameWidget = this.widgets.find((w) => w.name === "lora_name");

				if (loraNameWidget) {
					loraNameWidget.callback = (value) => {
						onLoraChanged(value);
					};
				}
			};
		}
	},
});