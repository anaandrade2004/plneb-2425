function delete_conceito(designation) {
    $.ajax("/conceitos/" + designation, {
        type: "DELETE",
        success: function(data) {
            console.log(data)
            if (data["success"]) {
                window.location.href = data["redirect_url"]
            }
        },
        error: function(error) {
            console.log(error)
        }
    })
}

$(document).ready(function() {
    var table = $('#tabela_conceitos').DataTable({
        search: {
            regex: true,  // Permite regex na busca
            smart: false // Desativa busca "inteligente" para regex puro
        }
    });

    // Aplica negrito nos resultados da busca
    table.on('draw.dt', function() {
        var searchTerm = table.search(); // Pega o termo da busca
        if (searchTerm === '') {
            // Remove todos os negritos se não houver busca
            $('td').html(function(_, html) {
                return html.replace(/<\/?strong>/g, '');
            });
            return;
        }

        try {
            // Cria o objeto RegExp com o termo de busca
            var regex = new RegExp(searchTerm, 'gi');
            
            // Percorre todas as células da tabela
            $('td').each(function() {
                var cell = $(this);
                var originalText = cell.text();
                
                // Guarda o HTML original para restaurar depois
                var originalHtml = cell.html();
                
                // Substitui todas as ocorrências pelo texto em negrito
                var highlightedHtml = originalText.replace(regex, function(match) {
                    return '<strong>' + match + '</strong>';
                });
                
                // Aplica as alterações apenas se houve correspondência
                if (highlightedHtml !== originalText) {
                    cell.html(highlightedHtml);
                } else {
                    // Restaura o HTML original se não houve correspondência
                    cell.html(originalHtml.replace(/<\/?strong>/g, ''));
                }
            });
        } catch (e) {
            console.error("Erro no regex:", e);
            // Se o regex for inválido, remove todos os negritos
            $('td').html(function(_, html) {
                return html.replace(/<\/?strong>/g, '');
            });
        }
    });
});