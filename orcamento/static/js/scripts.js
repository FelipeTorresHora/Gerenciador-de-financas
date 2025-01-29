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

            const ctx = document.getElementById("budgetChart").getContext("2d");
            new Chart(ctx, {
                type: "bar", // Tipo de gráfico
                data: {
                    labels: data.categories, // Categorias no eixo X
                    datasets: [
                        {
                            label: "Gastos", // Legenda do dataset
                            data: data.values, // Valores no eixo Y
                            backgroundColor: ["#ff6384", "#36a2eb", "#cc65fe", "#ffce56", "#4bc0c0"], // Cores das barras
                            borderColor: ["#ff6384", "#36a2eb", "#cc65fe", "#ffce56", "#4bc0c0"], // Cores das bordas
                            borderWidth: 1, // Largura da borda
                        },
                    ],
                },
                options: {
                    responsive: false, // Torna o gráfico responsivo
                    maintainAspectRatio: false, // Permite que o gráfico redimensione livremente
                    width: 600,
                    height: 400,
                    plugins: {
                        legend: {
                            display: true, // Exibe a legenda
                            position: "top", // Posição da legenda
                        },
                        tooltip: {
                            enabled: true, // Ativa tooltips
                            callbacks: {
                                label: function (context) {
                                    return `Valor: ${context.raw.toLocaleString("pt-BR", {
                                        style: "currency",
                                        currency: "BRL",
                                    })}`; // Formata o valor em Reais (BRL)
                                },
                            },
                        },
                    },
                    scales: {
                        y: {
                            beginAtZero: true, // Começa o eixo Y do zero
                            ticks: {
                                callback: function (value) {
                                    return value.toLocaleString("pt-BR", {
                                        style: "currency",
                                        currency: "BRL",
                                    }); // Formata os valores do eixo Y em Reais (BRL)
                                },
                            },
                        },
                    },
                },
            });
        })
        .catch((error) => {
            console.error("Erro ao atualizar gráfico:", error);
            alert("Erro ao carregar dados do gráfico.");
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

// Inicializar o gráfico ao carregar a página
document.addEventListener("DOMContentLoaded", updateChart);