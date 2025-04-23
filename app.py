import streamlit as st
from pyvis.network import Network
import json
import os
import tempfile

st.set_page_config(layout="wide")

st.title("🌌 Pat Bajari's Academic Constellation")
st.markdown("A Tribute to His Scholarly Legacy (1969–2025)")

# Load data
data_path = os.path.join("public", "full_data.json")
with open(data_path, "r") as f:
    data = json.load(f)

nodes = data["nodes"]
links = data["links"]

# Fix edge keys for vis.js compatibility
for link in links:
    link["from"] = link["source"]
    link["to"] = link["target"]

# Create Pyvis network
net = Network(height="800px", width="100%", bgcolor="#0a0a2a", font_color="white")
net.barnes_hut()

# Add nodes with color and shape logic
for node in nodes:
    if node["type"] == "central":
        color = "#FFD700"
        shape = "star"
    elif node["type"] == "coauthor":
        color = "#00C49A"
        shape = "dot"
    elif node["type"] == "institution":
        color = "#FF6F91"
        shape = "triangle"
    else:
        color = "#4DA6FF"
        shape = "dot"

    net.add_node(
        node["id"],
        label=node["label"],
        size=node.get("size", 10),
        title=node.get("label", ""),
        color=color,
        shape=shape,
        font={"size": 20, "color": "white"},
        shadow=True,
        year=node.get("year"),
        type=node.get("type")
    )

# Add edges using from/to
for link in links:
    net.add_edge(link["from"], link["to"], value=link["value"], color="#aaaaaa")

net.set_options("""
{
  "layout": {
    "improvedLayout": false
  },
  "nodes": { "shape": "dot", "shadow": true },
  "edges": {
    "color": { "color": "#aaaaaa" },
    "smooth": { "type": "dynamic" }
  },
  "physics": {
    "forceAtlas2Based": {
      "gravitationalConstant": -50,
      "centralGravity": 0.005,
      "springLength": 120,
      "springConstant": 0.08
    },
    "minVelocity": 0.75,
    "solver": "forceAtlas2Based"
  },
  "interaction": {
    "hover": true,
    "tooltipDelay": 100
  }
}
""")

with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".html") as tmp_file:
    net.save_graph(tmp_file.name)
    html_content = open(tmp_file.name, "r", encoding="utf-8").read()

    html_content = html_content.replace(
        '</body>',
        """
<div id=\"year-label\" style=\"position: absolute; top: 20px; right: 40px; font-size: 24px; font-weight: bold; color: white; background: rgba(0, 0, 0, 0.5); padding: 6px 14px; border-radius: 12px; z-index: 2; font-family: 'Courier New', monospace;\">Starting...</div>

<style>
#mynetwork {
    margin: 0;
    padding: 0;
    visibility: hidden;
    background: radial-gradient(ellipse at bottom, #1B2735 0%, #090A0F 100%);
    position: relative;
    overflow: hidden;
}
.star {
    position: absolute;
    background-color: white;
    border-radius: 50%;
    animation: twinkle 5s infinite;
    z-index: 0;
    pointer-events: none;
}
@keyframes twinkle {
    0% {opacity: 0.3;}
    50% {opacity: 1;}
    100% {opacity: 0.3;}
}
canvas {
    z-index: 1;
    position: relative;
}
</style>

<script>
document.addEventListener("DOMContentLoaded", function () {
    setTimeout(function () {
        const networkDiv = document.getElementById('mynetwork');
        if (networkDiv) {
            const width = networkDiv.offsetWidth;
            const height = networkDiv.offsetHeight;
            for (let i = 0; i < 300; i++) {
                const star = document.createElement('div');
                star.className = 'star';
                star.style.left = Math.random() * width + 'px';
                star.style.top = Math.random() * height + 'px';
                const size = 0.5 + Math.random() * 2.5;
                star.style.width = size + 'px';
                star.style.height = size + 'px';
                star.style.animationDelay = Math.random() * 5 + 's';
                star.style.opacity = Math.random() * 0.7 + 0.3;
                networkDiv.appendChild(star);
            }
        }
    }, 1000);
});
</script>

<script>
document.addEventListener("DOMContentLoaded", function () {
    setTimeout(function () {
        if (!window.network) return;

        const allNodes = [...network.body.data.nodes.get()];
        const allEdges = [...network.body.data.edges.get()];
        const nodes = network.body.data.nodes;
        const edges = network.body.data.edges;

        const pat = allNodes.find(n => n.type === "central");
        const papers = allNodes.filter(n => n.type === "paper" && typeof n.year === "number");
        const coauthors = allNodes.filter(n => n.type === "coauthor");
        const coauthorMap = Object.fromEntries(coauthors.map(c => [c.id, c]));

        nodes.clear();
        edges.clear();
        nodes.add(pat);
        document.getElementById("mynetwork").style.visibility = "visible";

        papers.sort((a, b) => a.year - b.year);

        const yearLabel = document.getElementById("year-label");
        let index = 0;

        function safeNode(n) {
          return {
            id: n.id, label: n.label, title: n.title, color: n.color,
            size: n.size, shape: n.shape, font: n.font, shadow: n.shadow
          };
        }

        function addNext() {
            if (index >= papers.length) {
                yearLabel.textContent = "✅ Complete";
                return;
            }

            const paper = papers[index];
            nodes.add(safeNode(paper));
            const connected = allEdges.filter(e => e.from === paper.id || e.to === paper.id);

            connected.forEach(edge => {
                const otherId = edge.from === paper.id ? edge.to : edge.from;
                if (coauthorMap[otherId] && !nodes.get(otherId)) {
                    nodes.add(safeNode(coauthorMap[otherId]));
                }
                edges.add(edge);
            });

            yearLabel.textContent = `📅 ${paper.year}`;
            index++;
            setTimeout(addNext, 1000);
        }

        addNext();
    }, 1000);
});
</script>
</body>""")

    with open(tmp_file.name, "w", encoding="utf-8") as f:
        f.write(html_content)

    tmp_file_path = tmp_file.name

st.components.v1.html(open(tmp_file_path, "r", encoding="utf-8").read(), height=850)

# with st.sidebar:
#     st.subheader("Legend")
#     st.markdown("<span style='color:#FFD700'>●</span> Pat Bajari", unsafe_allow_html=True)
#     st.markdown("<span style='color:#00C49A'>●</span> Co-authors", unsafe_allow_html=True)
#     st.markdown("<span style='color:#4DA6FF'>●</span> Publications", unsafe_allow_html=True)
#     st.markdown("<span style='color:#FF6F91'>●</span> Institutions", unsafe_allow_html=True)
#     st.markdown("\nData source: `no_inst_med.json`")
