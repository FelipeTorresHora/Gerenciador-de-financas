// Referências aos elementos
const tableBody = document.querySelector("#expensesTable tbody");
const addRowButton = document.getElementById("add-row");
const saveButton = document.getElementById("save-table");
const updateChartButton = document.getElementById("update-chart");

// Função para adicionar uma nova linha
function addRow() {
    const row = document.createElement("tr");
    row.innerHTML = `
        <td><input type="date" class="form-control"></td>
        <td><input type="text" class="form-control"></td>
        <td><input type="text" class="form-control"></td>
        <td><input type="number" class="form-control" min="0"></td>
        <td><button class="btn btn-danger btn-sm delete-row">Excluir</button></td>
    `;
    tableBody.appendChild(row);
}

// Função para excluir uma linha
function deleteRow(event) {
    if (event.target.classList.contains("delete-row")) {
        event.target.closest("tr").remove();
    }
}

// Função para salvar a tabela
function saveTable() {
    const rows = tableBody.querySelectorAll("tr");
    const data = [];

    rows.forEach((row) => {
        const cells = row.querySelectorAll("input");
        const rowData = {
            date: cells[0].value,
            description: cells[1].value,
            category: cells[2].value,
            value: parseFloat(cells[3].value) || 0,
        };

        // Validação para impedir valores negativos
        if (rowData.value < 0) {
            alert("Os valores não podem ser negativos.");
            return;
        }

        data.push(rowData);
    });

    // Enviar dados para o backend
    fetch("/save/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({ expenses: data }),
    }).then((response) => {
        if (response.ok) {
            alert("Tabela salva com sucesso!");
        } else {
            alert("Erro ao salvar tabela.");
        }
    });
}

// Função para atualizar os gráficos
function updateChart() {
    fetch("/update-chart/")
        .then((response) => response.json())
        .then((data) => {
            const chart = Chart.getChart("budgetChart");
            if (chart) {
                chart.destroy();
            }

            new Chart(document.getElementById("budgetChart").getContext("2d"), {
                type: "bar",
                data: {
                    labels: data.categories,
                    datasets: [
                        {
                            label: "Gastos",
                            data: data.values,
                            backgroundColor: ["#ff6384", "#36a2eb", "#cc65fe"],
                        },
                    ],
                },
            });
        });
}

// Obter token CSRF
function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]").value;
}

// Event Listeners
addRowButton.addEventListener("click", addRow);
tableBody.addEventListener("click", deleteRow);
saveButton.addEventListener("click", saveTable);
updateChartButton.addEventListener("click", updateChart);
