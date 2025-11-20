import { app } from "/scripts/app.js";
import { api } from "/scripts/api.js";
import { ComfyWidgets } from "/scripts/widgets.js";

async function onLoraChanged(node, lora_name) {
    try {
        const response = await api.fetchApi("/on_demand_loader/lora_changed", {
            method: "POST",
            body: JSON.stringify({ lora_name }),
            headers: {
                "Content-Type": "application/json",
            },
        });
        if (response.status !== 200) {
            console.error(`[ComfyUI-OnDemand-Loaders] Failed to notify backend of lora change: ${response.status}`);
        } else {
			const loraInfo = await response.json();
			addOrUpdateLoraInfoWidgets(node, loraInfo);
		}
    } catch (e) {
        console.error("[ComfyUI-OnDemand-Loaders] Failed to notify backend of lora change", e);
    }
}

function addOrUpdateLoraInfoWidgets(node, loraInfo) {
	if (loraInfo.name !== "None") {

		if (loraInfo.author) {
			const authorWidget = node.widgets.find((w) => w.name === "author");
			if (!authorWidget) {
				const w = ComfyWidgets["STRING"](node, "author", ["STRING", { multiline: false }], app).widget;
				w.inputEl.readOnly = true;
				w.inputEl.style.opacity = 0.8;
				w.value = loraInfo.author;
			} else {
				authorWidget.value = loraInfo.author;
				authorWidget.hidden = false;
			}
		}

		if (loraInfo.trigger_words) {
			const triggerWordsWidget = node.widgets.find((w) => w.name === "trigger_words");
			if (!triggerWordsWidget) {
				const w = ComfyWidgets["STRING"](node, "trigger_words", ["STRING", { multiline: true }], app).widget;
				w.inputEl.readOnly = true;
				w.inputEl.style.opacity = 0.8;
				w.value = loraInfo.trigger_words.join(', ');
			} else {
				triggerWordsWidget.value = loraInfo.trigger_words.join(', ');
				triggerWordsWidget.hidden = false;
			}
		}
		if (loraInfo.id) {
			const urlWidget = node.widgets.find((w) => w.name === "url");
			if (!urlWidget) {
				const w = ComfyWidgets["MARKDOWN"](node, "url", ["STRING", { multiline: false }], app).widget;
				w.inputEl.readOnly = true;
				w.inputEl.style.opacity = 0.8;
				w.value = `[Civitai Model URL](https://civitai.com/models/${loraInfo.id})`;
			} else {
				urlWidget.value = `[Civitai Model URL](https://civitai.com/models/${loraInfo.id})`;
				urlWidget.hidden = false;
			}
		}
	} else {
		const authorWidget = node.widgets.find((w) => w.name === "author");
		if (authorWidget) {
			authorWidget.hidden = true;
		}
		const triggerWordsWidget = node.widgets.find((w) => w.name === "trigger_words");
		if (triggerWordsWidget) {
			triggerWordsWidget.hidden = true;
		}
		const urlWidget = node.widgets.find((w) => w.name === "url");
		if (urlWidget) {
			urlWidget.hidden = true;
		}
	}
	node.computeSize();
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
						onLoraChanged(this, value);
					};
				}
				
				this.addWidget("button", "ℹ️ Lora Info", "", () => {
					window.showSelectedLoraInfo(this, loraNameWidget);
				}, { serialize: false });
				
			};
		}
	},
	async setup() {
        window.showSelectedLoraInfo = async (node, widget) => {
            onLoraChanged(node, widget.value);
			/*
            try {
                const response = await fetch("/on_demand_loader/get_selected_lora_info");
                if (response.ok) {
                    const loraInfo = await response.json();
					addOrUpdateLoraInfoWidgets(node, loraInfo);
                } else {
                    const errorData = await response.json();
                    alert(`Error fetching LoRA info: ${errorData.error || response.statusText}`);
                }
            } catch (error) {
                console.error("[ComfyUI-OnDemand-Loaders] Failed to fetch selected LoRA info:", error);
                alert("Failed to fetch selected LoRA info. Check console for details.");
            }
				*/
        };
    }
});