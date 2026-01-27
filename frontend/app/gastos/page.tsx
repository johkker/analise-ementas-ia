"use client";

import { useState, useEffect } from "react";
import { 
  ArrowUpRight,
  Search, 
  Filter, 
  ChevronLeft, 
  ChevronRight, 
  Receipt, 
  CircleAlert, 
  User, 
  Building2, 
  Calendar,
  Layers,
  Sparkles
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { fetchAPI } from "@/lib/api";

export default function GastosExploration() {
  const [items, setItems] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  
  // Filters
  const [nome, setNome] = useState("");
  const [partido, setPartido] = useState("");
  const [tipo, setTipo] = useState("");
  const [mes, setMes] = useState("all");

  const fetchData = async () => {
    setLoading(true);
    try {
      let url = `/gastos/exploration?page=${page}&page_size=12`;
      if (nome) url += `&politico_nome=${nome}`;
      if (partido && partido !== "all") url += `&sigla_partido=${partido}`;
      if (tipo && tipo !== "all") url += `&tipo_despesa=${tipo}`;
      if (mes && mes !== "all") url += `&mes=${mes}`;

      const data = await fetchAPI(url);
      setItems(data.items);
      setTotal(data.total);
    } catch (error) {
      console.error("Failed to fetch expenses:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [page, partido, tipo, mes]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchData();
  };

  return (
    <div className="space-y-8 pb-20">
      <div className="flex flex-col space-y-4">
        <h1 className="text-4xl font-heading font-black tracking-tighter flex items-center gap-3">
          <Receipt className="w-10 h-10 text-primary" /> Auditoria de Gastos
        </h1>
        <p className="text-muted-foreground font-medium max-w-2xl">
          Explore cada centavo da cota parlamentar. Filtre por nomes, partidos ou categorias e veja onde o dinheiro público está sendo aplicado.
        </p>
      </div>

      {/* Filters Bar */}
      <Card className="glass border-white/5 p-4 rounded-3xl">
        <form onSubmit={handleSearch} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="relative col-span-1 lg:col-span-2">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input 
              placeholder="Buscar por nome do deputado..." 
              className="pl-10 glass-hover border-white/10 rounded-xl h-12"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
            />
          </div>

          <select 
            value={partido} 
            onChange={(e) => setPartido(e.target.value)}
            className="flex h-12 w-full rounded-xl border border-white/10 bg-white/5 backdrop-blur-md px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 appearance-none glass-hover cursor-pointer"
          >
            <option value="all" className="bg-slate-900">Todos os Partidos</option>
            <option value="PT" className="bg-slate-900">PT</option>
            <option value="PL" className="bg-slate-900">PL</option>
            <option value="PP" className="bg-slate-900">PP</option>
            <option value="UNIÃO" className="bg-slate-900">UNIÃO</option>
            <option value="MDB" className="bg-slate-900">MDB</option>
            <option value="PSD" className="bg-slate-900">PSD</option>
            <option value="PSOL" className="bg-slate-900">PSOL</option>
          </select>

          <select 
            value={tipo} 
            onChange={(e) => setTipo(e.target.value)}
            className="flex h-12 w-full rounded-xl border border-white/10 bg-white/5 backdrop-blur-md px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 appearance-none glass-hover cursor-pointer"
          >
            <option value="all" className="bg-slate-900">Todos os Tipos</option>
            <option value="COMBUSTÍVEIS" className="bg-slate-900">Combustíveis</option>
            <option value="TELEFONIA" className="bg-slate-900">Telefonia</option>
            <option value="DIVULGAÇÃO" className="bg-slate-900">Divulgação</option>
            <option value="ALIMENTAÇÃO" className="bg-slate-900">Alimentação</option>
            <option value="HOSPEDAGEM" className="bg-slate-900">Hospedagem</option>
            <option value="PASSAGENS" className="bg-slate-900">Passagens</option>
          </select>

          <Button type="submit" className="bg-primary hover:bg-emerald-500 h-12 font-bold rounded-xl gap-2">
            <Filter className="w-4 h-4" /> Filtrar
          </Button>
        </form>
      </Card>

      {/* Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-64 glass rounded-3xl animate-pulse" />
          ))}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {items.map((gasto) => (
              <Card key={gasto.id} className="glass group hover:border-primary/40 transition-all cursor-pointer overflow-hidden relative">
                {gasto.ai_resumo && (
                  <div className="absolute top-0 right-0 p-3 z-10">
                    <div className="bg-primary/20 backdrop-blur-md rounded-lg p-1.5 border border-primary/30" title="Analise por IA disponível">
                       <Sparkles className="w-3.5 h-3.5 text-primary animate-pulse" />
                    </div>
                  </div>
                )}
                <CardContent className="p-6 space-y-4">
                  <div className="flex justify-between items-start">
                    <div className="space-y-1">
                      <p className="text-[10px] uppercase font-black tracking-widest text-muted-foreground flex items-center gap-1">
                        <User className="w-3 h-3" /> {gasto.politico}
                      </p>
                      <h3 className="font-bold text-lg leading-tight line-clamp-1">{gasto.tipo}</h3>
                    </div>
                    <Badge variant="outline" className="border-white/10 bg-white/5 font-black text-[10px]">{gasto.partido}</Badge>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center gap-2 text-xs text-muted-foreground font-medium">
                       <Building2 className="w-3.5 h-3.5" /> 
                       <span className="truncate">{gasto.fornecedor || "CNPJ não informado"}</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground font-medium">
                       <Calendar className="w-3.5 h-3.5" /> 
                       <span>{new Date(gasto.data).toLocaleDateString('pt-BR')}</span>
                    </div>
                  </div>

                  <div className="pt-4 border-t border-white/5 flex items-center justify-between">
                    <div className="flex flex-col">
                        <span className="text-[10px] font-black uppercase text-muted-foreground">Valor Bruto</span>
                        <span className="text-2xl font-black font-heading text-foreground">
                            R$ {gasto.valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                        </span>
                    </div>
                    <Button variant="ghost" size="icon" className="group-hover:text-primary transition-colors">
                        <ArrowUpRight className="w-5 h-5" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between pt-8">
            <p className="text-sm text-muted-foreground font-medium">
               Mostrando <span className="font-bold text-foreground">{(page - 1) * 12 + 1}</span> - <span className="font-bold text-foreground">{Math.min(page * 12, total)}</span> de <span className="font-bold text-foreground">{total}</span> registros
            </p>
            <div className="flex items-center gap-2">
              <Button 
                variant="outline" 
                size="icon" 
                className="glass-hover border-white/10"
                disabled={page === 1}
                onClick={() => setPage(p => Math.max(1, p - 1))}
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <Button 
                variant="outline" 
                size="icon" 
                className="glass-hover border-white/10"
                disabled={page * 12 >= total}
                onClick={() => setPage(p => p + 1)}
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </>
      )}

      {items.length === 0 && !loading && (
        <div className="py-20 text-center flex flex-col items-center justify-center space-y-4">
           <Layers className="w-16 h-16 text-muted/30" />
           <p className="text-muted-foreground font-medium">Nenhum gasto encontrado para os filtros selecionados.</p>
           <Button variant="link" onClick={() => {setNome(""); setPartido("all"); setTipo("all");}}>Limpar Filtros</Button>
        </div>
      )}
    </div>
  );
}
