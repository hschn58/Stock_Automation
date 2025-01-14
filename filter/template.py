
template = r"""
<!doctype html>
<html>
  <head>
    <title>SCM Advent Filter (Multi-Filter + Sorting)</title>
    <style>
      .container { display: flex; }
      .left-panel { width: 60%; margin-right: 20px; }
      .right-panel { width: 40%; }
      table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
        padding: 5px;
        text-align: center;
      }
      th { background-color: #f2f2f2; }
      td.clickable:hover { background-color: #f0f0f0; cursor: pointer; }
    </style>
  </head>
  <body>
    <!-- MAIN FILTER FORM -->
    <form method="POST">
      <input type="hidden" name="action" value="filter">
      <h3>SCM Advent Filter</h3>

      <!-- First Filter -->
      <label for="classFilter1">Class #1:</label>
      <select id="classFilter1" name="classFilter1">
      {% for i in range(cached_classes|length) %}
          {% set full_class = cached_classes[i] %}
          {% set short_class = short_class_names[i] %}
          <option value="{{ full_class }}"
                  {% if full_class == selected_class1 %}selected{% endif %}>
              {{ full_class }} ({{ short_class }})
          </option>
      {% endfor %}
      </select>
      <select name="operator1">
        <option value="lt" {% if operator1 == 'lt' %}selected{% endif %}>&lt;</option>
        <option value="gt" {% if operator1 == 'gt' %}selected{% endif %}>&gt;</option>
        <option value="eq" {% if operator1 == 'eq' %}selected{% endif %}>= (±3%)</option>
      </select>
      <input type="number" step="any" name="targetPercent1" placeholder="30" required value="{{ target_percent1 }}">
      <br><br>
     
    <div id="secondFilterSection" style="display: none;">
      <!-- Second Filter -->
      <label for="classFilter2">Class #2:</label>
      <select id="classFilter2" name="classFilter2">
        {% for i in range(cached_classes|length) %}
          {% set full_class = cached_classes[i] %}
          {% set short_class = short_class_names[i] %}
          <option value="{{ full_class }}"
                  {% if full_class == selected_class2 %}selected{% endif %}>
              {{ full_class }} ({{ short_class }})
          </option>
      {% endfor %}
      </select>
      <select name="operator2">
          <option value="lt" {% if operator2 == 'lt' %}selected{% endif %}>&lt;</option>
          <option value="gt" {% if operator2 == 'gt' %}selected{% endif %}>&gt;</option>
          <option value="eq" {% if operator2 == 'eq' %}selected{% endif %}>= (±3%)</option>
      </select>
      <input type="number" step="any" name="targetPercent2" id="targetPercent2" placeholder="30" value="{{ target_percent2 }}">
    </div>

    <!-- Checkbox to enable the second filter -->
    <input type="checkbox" id="use_second_filter" name="use_second_filter" 
        {% if use_second_filter %}checked{% endif %}>
    <label for="use_second_filter">Use Second Filter?</label>
      <div id="sectorFilterSection" style="display: none;">
      <br><br>
      <label for="sectorFilter">Sector Filter:</label>
      <select id="sectorFilter" name="sectorFilter" onchange="updateTargetPercentRequirement()">
          <option value="">(none)</option>
          {% for seg in cached_segments %}
          <option value="{{ seg }}" {% if seg == selected_sector %}selected{% endif %}>{{ seg }}</option>
          {% endfor %}
      </select>
      <select name="operator_sector">
          <option value="lt" {% if operator_sector == 'lt' %}selected{% endif %}>&lt;</option>
          <option value="gt" {% if operator_sector == 'gt' %}selected{% endif %}>&gt;</option>
          <option value="eq" {% if operator_sector == 'eq' %}selected{% endif %}>= (±3%)</option>
      </select>
      <input
          type="number"
          step="any"
          name="targetPercentSector"
          id="targetPercentSector"
          placeholder="30"
          value="{{ target_percent_sector }}"
      >
      </div>
      <br><br>
      <button type="submit">Apply Filter</button>
    </form>

    <!-- Hidden field to persist last_sort across chart clicks or re-filters -->
    <input type="hidden" id="saved_last_sort" value="{{ last_sort }}">

    <div class="container">
      <div class="left-panel" style="margin: 0; padding: 0;">
        {% if hits %}
          <h3>Filter Results</h3>
          <!-- Add this block -->
          <div style="display:flex; gap:30px; margin-bottom:10px;">
              <div style="border:1px solid #ccc; padding:10px;">
              <strong>Portfolios:</strong> {{ total_portfolios }}
              </div>
              <div style="border:1px solid #ccc; padding:10px;">
              <strong>Accounts:</strong> {{ total_accounts }}
              </div>
          </div>


          <!-- SORT BUTTONS (carry forward all filter params including 2nd filter usage + sector filter) -->
          <!-- Sort by Class #1 -->
          <form method="POST" style="display:inline;">
            <input type="hidden" name="action" value="sort_class1">
            <input type="hidden" name="classFilter1" value="{{ selected_class1 }}">
            <input type="hidden" name="operator1" value="{{ operator1 }}">
            <input type="hidden" name="targetPercent1" value="{{ target_percent1 }}">
            <input type="hidden" name="classFilter2" value="{{ selected_class2 }}">
            <input type="hidden" name="operator2" value="{{ operator2 }}">
            <input type="hidden" name="targetPercent2" value="{{ target_percent2 }}">
            <input type="hidden" name="use_second_filter" value="{{ 'on' if use_second_filter else '' }}">
            <input type="hidden" name="sectorFilter" value="{{ selected_sector }}">
            <input type="hidden" name="operator_sector" value="{{ operator_sector }}">
            <input type="hidden" name="targetPercentSector" value="{{ target_percent_sector }}">
            <input type="hidden" name="last_sort" value="sort_class1">
            <button type="submit">Order by {{ selected_class1 }}</button>
          </form>

          <!-- Sort by Class #2 -->
          {% if use_second_filter %}
            <form method="POST" style="display:inline; margin-left:10px;">
                <input type="hidden" name="action" value="sort_class2">
                <input type="hidden" name="classFilter1" value="{{ selected_class1 }}">
                <input type="hidden" name="operator1" value="{{ operator1 }}">
                <input type="hidden" name="targetPercent1" value="{{ target_percent1 }}">
                <input type="hidden" name="classFilter2" value="{{ selected_class2 }}">
                <input type="hidden" name="operator2" value="{{ operator2 }}">
                <input type="hidden" name="targetPercent2" value="{{ target_percent2 }}">
                <input type="hidden" name="use_second_filter" value="{{ 'on' if use_second_filter else '' }}">
                <input type="hidden" name="sectorFilter" value="{{ selected_sector }}">
                <input type="hidden" name="operator_sector" value="{{ operator_sector }}">
                <input type="hidden" name="targetPercentSector" value="{{ target_percent_sector }}">
                <input type="hidden" name="last_sort" value="sort_class2">
                <button type="submit">Order by {{ selected_class2 }} </button>
            </form>
          {% endif %}

          <!-- Sort by Sector Filter -->
          {% if sector %}
            <form method="POST" style="display:inline; margin-left:10px;">
              <input type="hidden" name="action" value="sort_sector">
              <input type="hidden" name="classFilter1" value="{{ selected_class1 }}">
              <input type="hidden" name="operator1" value="{{ operator1 }}">
              <input type="hidden" name="targetPercent1" value="{{ target_percent1 }}">
              <input type="hidden" name="classFilter2" value="{{ selected_class2 }}">
              <input type="hidden" name="operator2" value="{{ operator2 }}">
              <input type="hidden" name="targetPercent2" value="{{ target_percent2 }}">
              <input type="hidden" name="use_second_filter" value="{{ 'on' if use_second_filter else '' }}">
              <input type="hidden" name="sectorFilter" value="{{ selected_sector }}">
              <input type="hidden" name="operator_sector" value="{{ operator_sector }}">
              <input type="hidden" name="targetPercentSector" value="{{ target_percent_sector }}">
              <input type="hidden" name="last_sort" value="sort_sector">
              <button type="submit">Order by {{ selected_sector }}</button>
            </form>
          {% endif %}

          <!-- Sort by Cash -->
          <form method="POST" style="display:inline; margin-left:10px;">
            <input type="hidden" name="action" value="sort_cash">
            <input type="hidden" name="classFilter1" value="{{ selected_class1 }}">
            <input type="hidden" name="operator1" value="{{ operator1 }}">
            <input type="hidden" name="targetPercent1" value="{{ target_percent1 }}">
            <input type="hidden" name="classFilter2" value="{{ selected_class2 }}">
            <input type="hidden" name="operator2" value="{{ operator2 }}">
            <input type="hidden" name="targetPercent2" value="{{ target_percent2 }}">
            <input type="hidden" name="use_second_filter" value="{{ 'on' if use_second_filter else '' }}">
            <input type="hidden" name="sectorFilter" value="{{ selected_sector }}">
            <input type="hidden" name="operator_sector" value="{{ operator_sector }}">
            <input type="hidden" name="targetPercentSector" value="{{ target_percent_sector }}">
            <input type="hidden" name="last_sort" value="sort_cash">
            <button type="submit">Order by Cash</button>
          </form>

          <form method="POST" style="display:inline; margin-left:10px;">
            <input type="hidden" name="action" value="download_excel">
            <input type="hidden" name="classFilter1" value="{{ selected_class1 }}">
            <input type="hidden" name="operator1" value="{{ operator1 }}">
            <input type="hidden" name="targetPercent1" value="{{ target_percent1 }}">
            <input type="hidden" name="classFilter2" value="{{ selected_class2 }}">
            <input type="hidden" name="operator2" value="{{ operator2 }}">
            <input type="hidden" name="targetPercent2" value="{{ target_percent2 }}">
            <input type="hidden" name="use_second_filter" value="{{ 'on' if use_second_filter else '' }}">
            <input type="hidden" name="sectorFilter" value="{{ selected_sector }}">
            <input type="hidden" name="operator_sector" value="{{ operator_sector }}">
            <input type="hidden" name="targetPercentSector" value="{{ target_percent_sector }}">
            <input type="hidden" name="last_sort" value="{{ last_sort }}">
            <button type="submit">Download to Excel</button>
          </form>

          <br><br>

          <table>
            <thead>
              <tr>
                <th>Portfolio Name</th>
                <th>Short Name</th>
                <th>{{ short_class_names[cached_classes.index(selected_class1)] }}</th>
                {% if use_second_filter %}
                  <th>
                    {% if selected_class2 in cached_classes %}
                      {{ short_class_names[cached_classes.index(selected_class2)] }}
                    {% endif %}
                  </th>
                {% endif %}
                {% if sector %}
                  <th>Sector</th>
                {% endif %}
                <th>Account Number</th>
                <th>Cash</th>
                <th>Portfolio Value</th>
              </tr>
            </thead>
            <tbody>
              {% for h in hits %}
                {% set rowSpan = h.cashRows|length if h.cashRows else 1 %}
                {% for i in range(rowSpan) %}
                  <tr>
                    {% if i == 0 %}
                      <td class="clickable" rowspan="{{ rowSpan }}"
                          onclick="postChart('{{ h.portfolio|escape }}', '{{ h.shortName|escape }}')">
                        {{ h.portfolio }}
                      </td>
                      <td class="clickable" rowspan="{{ rowSpan }}"
                          onclick="postChart('{{ h.portfolio|escape }}', '{{ h.shortName|escape }}')">
                        {{ h.shortName }}
                      </td>
                      <!-- Show Class #1 %, Class #2 %, Sector % -->
                      <td class="clickable" rowspan="{{ rowSpan }}"
                          onclick="postChart('{{ h.portfolio|escape }}', '{{ h.shortName|escape }}')">
                        {{ h.percent1|round(2) }}%
                      </td>
                      {% if use_second_filter %}
                        <td class="clickable" rowspan="{{ rowSpan }}"
                            onclick="postChart('{{ h.portfolio|escape }}', '{{ h.shortName|escape }}')">
                          {{ h.percent2|round(2) }}%
                        </td>
                      {% endif %}

                      {% if sector %}
                        <td class="clickable" rowspan="{{ rowSpan }}"
                            onclick="postChart('{{ h.portfolio|escape }}', '{{ h.shortName|escape }}')">
                          {{ h.sectorPercent|round(2) }}%
                        </td>
                      {% endif %}
                    {% endif %}
                    {% if h.cashRows and i < (h.cashRows|length) %}
                      <td>{{ h.cashRows[i].accountNumber }}</td>
                      <td>{{ "${:,.2f}".format(h.cashRows[i].marketValue) }}</td>
                    {% else %}
                      <td></td><td></td>
                    {% endif %}
                    {% if i == 0 %}
                      <td class="clickable" rowspan="{{ rowSpan }}"
                          onclick="postChart('{{ h.portfolio|escape }}', '{{ h.shortName|escape }}')">
                        {{"${:,.2f}".format(h.portfolioValue|default('N/A')) }}
                      </td>
                    {% endif %}
                  </tr>
                {% endfor %}
              {% endfor %}
            </tbody>
          </table>
        {% elif message %}
          <p><strong>{{ message }}</strong></p>
        {% endif %}
      </div>

      <div class="right-panel" style="margin: 0; padding: 0;">
      <!-- Show 2 pie charts if both images are present -->
      {% if image_data %}
          <h3 style="text-align:center; margin: 5px 0;">Asset Breakdown - {{ chart_shortname }}</h3>
          <img src="data:image/png;base64,{{ image_data }}" alt="Pie Chart" style="display: block; margin: 0 auto;" />
      {% endif %}
    
      {% if image_data_sector %}
          <h3 style="text-align:center; margin: 5px 0;">Common Stock by Sector - {{ chart_shortname }}</h3>
          <img src="data:image/png;base64,{{ image_data_sector }}" alt="Pie Chart Sector" style="display: block; margin: 0 auto;" />
      {% endif %}
      </div>
    </div>

    <!-- JS to post for chart clicks, carrying all filter data + last_sort -->
    <script>
      function postChart(portfolio, shortName) {
        // We gather same data plus 'last_sort'
        var lastSort = document.getElementById('saved_last_sort').value;

        var form = document.createElement('form');
        form.method = 'POST'; 
        form.style.display = 'none';

        // action
        var a = document.createElement('input');
        a.type = 'hidden';
        a.name = 'action';
        a.value = 'view_chart';
        form.appendChild(a);

        // chart_portfolio / chart_shortname
        var p = document.createElement('input');
        p.type = 'hidden';
        p.name = 'chart_portfolio';
        p.value = portfolio;
        form.appendChild(p);

        var s = document.createElement('input');
        s.type = 'hidden';
        s.name = 'chart_shortname';
        s.value = shortName;
        form.appendChild(s);

        // leftover filter fields
        form.appendChild(hiddenField('classFilter1', '{{ selected_class1 }}'));
        form.appendChild(hiddenField('operator1', '{{ operator1 }}'));
        form.appendChild(hiddenField('targetPercent1', '{{ target_percent1 }}'));

        form.appendChild(hiddenField('classFilter2', '{{ selected_class2 }}'));
        form.appendChild(hiddenField('operator2', '{{ operator2 }}'));
        form.appendChild(hiddenField('targetPercent2', '{{ target_percent2 }}'));
        form.appendChild(hiddenField('use_second_filter', '{{ 'on' if use_second_filter else '' }}'));

        // carry sector filter if set
        form.appendChild(hiddenField('sectorFilter', '{{ selected_sector }}'));
        form.appendChild(hiddenField('operator_sector', '{{ operator_sector }}'));
        form.appendChild(hiddenField('targetPercentSector', '{{ target_percent_sector }}'));

        form.appendChild(hiddenField('last_sort', lastSort));

        document.body.appendChild(form);
        form.submit();
      }

      function hiddenField(nm, val) {
        var x = document.createElement('input');
        x.type = 'hidden';
        x.name = nm;
        x.value = val;
        return x;
      }
    </script>

    <script>
    function toggleSecondFilter() {
        const useSecondFilter = document.getElementById('use_second_filter').checked;
        const secondFilterSection = document.getElementById('secondFilterSection');
        const targetPercent2 = document.getElementById('targetPercent2');

        if (useSecondFilter) {
        secondFilterSection.style.display = 'block';
        targetPercent2.setAttribute('required', 'required');
        } else {
        secondFilterSection.style.display = 'none';
        targetPercent2.removeAttribute('required');
        }
    }

    // Attach the function to the checkbox
    document.addEventListener('DOMContentLoaded', function () {
        const useSecondFilterCheckbox = document.getElementById('use_second_filter');
        useSecondFilterCheckbox.addEventListener('change', toggleSecondFilter);
        toggleSecondFilter(); // Initial check on page load
    });
    </script>

    <script>
    function updateTargetPercentRequirement() {
        const sectorFilter = document.getElementById('sectorFilter');
        const targetPercentSector = document.getElementById('targetPercentSector');

        if (sectorFilter.value && sectorFilter.value !== '(none)') {
        targetPercentSector.setAttribute('required', 'required');
        } else {
        targetPercentSector.removeAttribute('required');
        }
    }

    // Call the function on page load to ensure the correct state is set
    document.addEventListener('DOMContentLoaded', updateTargetPercentRequirement);
    </script>

    <script>
    function toggleSectorFilter() {
        const classFilter1 = document.getElementById('classFilter1').value;
        const classFilter2 = document.getElementById('classFilter2').value;
        const sectorFilterSection = document.getElementById('sectorFilterSection');

        // Show the sector filter if either class is "COMMON STOCK"
        if (classFilter1 === 'COMMON STOCK' || classFilter2 === 'COMMON STOCK') {
        sectorFilterSection.style.display = 'block';
        } else {
        sectorFilterSection.style.display = 'none';
        }
    }

    // Attach the function to both dropdowns
    document.addEventListener('DOMContentLoaded', function () {
        document.getElementById('classFilter1').addEventListener('change', toggleSectorFilter);
        document.getElementById('classFilter2').addEventListener('change', toggleSectorFilter);
        toggleSectorFilter(); // Initial check on page load
    });
    </script>

  </body>
</html>
"""