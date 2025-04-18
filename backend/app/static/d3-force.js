const drug1_id = 25;
const drug2_id = 88;

fetch(`/graph_data?drug1_id=${drug1_id}&drug2_id=${drug2_id}`)
  .then(response => response.json())
  .then(data => {
    d3.select("#loading").style("display", "none");
    d3.select("svg").style("display", "block");

    const svg = d3.select("svg");
    const width = +svg.attr("width");
    const height = +svg.attr("height");

    const linkForce = d3.forceLink(data.links)
      .id(d => d.id)
      .distance(100)
      .strength(0.9);

    const simulation = d3.forceSimulation(data.nodes)
      .force("link", linkForce)
      .force("charge", d3.forceManyBody().strength(-150))
      .force("center", d3.forceCenter(600 / 2, 600 / 2));

    const link = svg.selectAll("line")
      .data(data.links)
      .enter()
      .append("line")
      .attr("stroke-width", d => 2 + d.weight * 5)
      .attr("stroke", "#999");

    const node = svg.selectAll("circle")
      .data(data.nodes)
      .enter()
      .append("circle")
      .attr("r", 8)
      .attr("fill", d => d.id === String(drug1_id) || d.id === String(drug2_id) ? "#d33" : "#69b3a2")
      .call(drag(simulation));

    const label = svg.selectAll("text")
      .data(data.nodes)
      .enter()
      .append("text")
      .text(d => d.id)
      .attr("x", 12)
      .attr("y", ".31em");

    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);

      label
        .attr("x", d => d.x + 8)
        .attr("y", d => d.y);
    });

    function drag(simulation) {
      return d3.drag()
        .on("start", (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on("drag", (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on("end", (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        });
    }
  });
